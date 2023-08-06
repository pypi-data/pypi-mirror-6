import json
import os
import sys
import re

from fig.cli.command import Command
from fig.packages.docker import Client
from fig.project import Project
from prettytable import PrettyTable

from jinja2 import Environment as JinjaEnv, StrictUndefined, PackageLoader, FileSystemLoader
import yaml


class FicloudServer():
    def __init__(self):
        self.client = Client()
        self.balancer_root = ''

    def _get_git_dir(self):
        return os.path.expanduser('~/apps')

    def _get_app_git_dir(self, name):
        return '%s/%s' % (self._get_git_dir(), name)

    def _get_deployment_dir(self):
        return os.path.expanduser('~/deploy')

    def _get_app_deployment_dir(self, name, version):
        return '%s/%s/%s' % (self._get_deployment_dir(), name, version)

    def _get_apps_conf_dir(self):
        return os.path.expanduser('~/apps-conf')

    def format_domain_config_path(self, domain_name):
        conf_dir = self._get_apps_conf_dir()
        if not os.path.exists(conf_dir):
            os.mkdir(conf_dir)
        return '%s/%s.conf' % (conf_dir, domain_name)

    def create_app(self, name, **kwargs):
        """
        Creates new application. Basically, creates new git repo.

        """
        repo_dir = self._get_app_git_dir(name)

        if not os.path.exists(repo_dir):
            os.system('git init --bare %s' % repo_dir)
            with open('%s/hooks/post-receive' % repo_dir, 'w') as f:
                f.write('#!/bin/bash\n'
                        '/home/alex/dev/ficloud/.env/bin/ficloud-server git-post-receive')
            os.system('chmod +x %s/hooks/post-receive' % repo_dir)
        else:
            print('Application already created')

    def remove_app(self, name, **kwargs):
        """
        Creates new application. Basically, creates new git repo.

        """
        repo_dir = self._get_app_git_dir(name)

        if not os.path.exists(repo_dir):
            print('Application not exist')
        else:
            os.system('rm -rf %s' % repo_dir)

    def deploy_app(self, name, version, **kwargs):
        """
        Creates new application. Basically, creates new git repo.

        """
        repo_dir = self._get_app_git_dir(name)
        target_dir = self._get_app_deployment_dir(name, version)

        if os.path.exists(target_dir):
            os.system('rm -rf %s' % target_dir)

        os.system('git clone -b %s %s %s' % (version, repo_dir, target_dir))

        self.ficloud_app_command(name, version, 'up -d')


    def ficloud_app_command(self, name, version, command, **kwargs):
        """
        Creates new application. Basically, creates new git repo.

        """
        target_dir = self._get_app_deployment_dir(name, version)

        app_name = '%s0%s' % (name, version)

        os.chdir(target_dir)
        os.system('ficloud fig --name=%s --env=%s \'%s\'' % (app_name, version, command))


    def list_apps(self, **kwargs):

        table = PrettyTable(["App", "Version", "State"])

        if os.path.exists(self._get_git_dir()):
            last_app = None

            for app in os.listdir(self._get_git_dir()):
                app_dir = self._get_deployment_dir() + '/' + app

                if os.path.exists(app_dir):
                    for version in os.listdir(app_dir):
                        project = self._get_fig_project(app, version)

                        status = {}
                        for service in project.get_services():
                            if len(service.containers()):
                                s = []
                                for ct in service.containers(stopped=True):
                                    if ct.is_running:
                                        s.append('UP[%s]' % (','.join(ct.inspect()['NetworkSettings']['Ports'].keys())))
                                    else:
                                        s.append('DOWN')

                                status[service.name] = ','.join(s)
                            else:
                                status[service.name] = 'DOWN'
                        app_status = ''
                        for service, st in status.items():
                            app_status += '%s=%s ' % (service, st)

                        table.add_row(('' if last_app == app else app, version, app_status))
                        last_app = app
                else:
                    table.add_row((app, '-', 'NOT DEPLOYED'))

        print(table)

    def _get_fig_project(self, app_name, app_version):
        config = yaml.load(open('%s/fig.yml' % self._get_app_deployment_dir(app_name, app_version)))
        project_name = '%s0%s' % (app_name, app_version)
        project = Project.from_config(project_name, config, self.client)
        return project

    def get_balancer_destinations(self, app_name, app_version, service, port):

        project = self._get_fig_project(app_name, app_version)

        service_ports = []
        for c in project.get_service(service).containers():
            if c.is_running:
                ports = c.inspect()['NetworkSettings']['Ports']
                service_ports.append(('127.0.0.1', int(ports['%s/tcp' % port][0]['HostPort'])))

        return service_ports

    def balancer_remove(self, domain, **kwargs):
        os.unlink(self.format_domain_config_path(domain))

    def balancer_set(self, domain, path, **kwargs):

        p = re.compile(r'^[\w\-\._]+$')
        result = p.match(domain)

        if not result:
            print('\nEnter valid domain name\n')
            sys.exit(1)

        p = re.compile(r'^([\w\-]+):(\d+)@([\w\-]+)#([\w\-]+)$')
        result = p.match(path)

        if not result:
            print('\nPath should be in form: service:port@appname#app_version\n')
            sys.exit(1)

        app_name = result.group(3)
        app_version = result.group(4)
        service_name = result.group(1)
        service_port = result.group(2)

        destinations = self.get_balancer_destinations(app_name, app_version, service_name, service_port)
        if not destinations:
            print('Looks like application is not running')
            sys.exit(1)

        config = {
            'target': path,
            'domain': domain,
            'app_name': app_name,
            'app_version': app_version,
            'backends': destinations
        }

        with open(self.format_domain_config_path(domain), 'w+') as f:
            json.dump(config, f)

    def balancer_list(self, **kwargs):

        table = PrettyTable(["Domain", "Target", "Resolved backends"])
        if os.path.exists(self._get_apps_conf_dir()):
            for conf_file in [x for x in os.listdir(self._get_apps_conf_dir()) if x.endswith('.conf')]:
                with open(self._get_apps_conf_dir() + '/' + conf_file) as f:
                    conf = json.load(f)
                    table.add_row(
                        (conf['domain'], conf['target'], ', '.join(['%s:%s' % tuple(x) for x in conf['backends']])))

        print(table)

    def balancer_dump(self, source, path, **kwargs):

        context = {}

        full_conf = {}

        if os.path.exists(source):
            for conf_file in [x for x in os.listdir(source) if x.endswith('.conf')]:
                with open(source + '/' + conf_file) as f:
                    conf = json.load(f)
                    full_conf[conf['domain']] = {
                        'name': re.sub('[^a-z0-9_]', '_', conf['domain']),
                        'domains': [conf['domain']],
                        'backends': [{
                                         'name': 'backend_%s' % i,
                                         'ip': x[0],
                                         'port': x[1]
                                     } for i, x in enumerate(conf['backends'])]
                    }

        context['apps'] = full_conf.values()

        engine = JinjaEnv(
            loader=FileSystemLoader('/etc/haproxy'),
            undefined=StrictUndefined
        )

        with open(path, 'w') as f:
            f.write(engine.get_template('haproxy.cfg.tpl').render(context))

        os.system('service haproxy reload')


    def git_post_receive(self, **kwargs):
        """
        Command is used inside git's post-receive hook
        """
        #!/home/alex/dev/ficloud/.env/bin/python

        p = re.compile(r'refs/heads/([^\s]+)')

        data = sys.stdin.read()
        print('>>%s<<' % data)
        m = p.search(data)
        if m:
            branch = m.group(1)
            app_name = os.path.basename(os.getcwd())
            print('\n\nDeploying app %s version %s ..\n\n' % (app_name, branch))

            self.deploy_app(app_name, branch)
        else:
            print('\n\nNB! No branch to deploy!\n\n')








