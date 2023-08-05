# Deployment for project {{ project_name }}
# generated at {{ datetime }}

from easyfab import BaseDeployment
from easyfab import items
import fabric.api


class Deployment(BaseDeployment):
    # list of all hosts
    hosts = ('127.0.0.1', )

    # @TODO: all management tasks will be running on this host only
    master_host = '127.0.0.1'

    # target directory on remote servers
    target_dir = '/www/{{ project_name }}/'

    # remote directory where manage.py is located (relative to project dir)
    manage_dir = 'src/{{ project_name }}/'

    # local directory where manage.py is located (relative to project dir)
    local_manage_dir = 'src/{{ project_name }}/'

    # path to target virtualenv
    virtualenv_dir = '/www/virtualenv/{{ project_name }}'

    # which files will be processed as templates
    processed_extensions = ['.py', '.html', '.conf']

    def get_items(self, context, **options):
        """ You have to yield items
            from easyfab.items
        """
        # create directories
        yield items.CreateDirItem('log')
        yield items.CreateDirItem('conf')
        yield items.CreateDirItem('static')
        yield items.CreateDirItem('media')
        #yield items.CopyItem(
        #    'src/{{ project_name }}', context['package_project_dir'].child('src')
        #)
        #yield items.SymlinkItem(
        #    'conf/supervisor.conf',
        #    '/etc/supervisor/conf.d/{{ project_name }}.conf'
        #)
        #yield items.SymlinkItem(
        #    'conf/nginx.conf',
        #    '/etc/nginx/conf.d/{{ project_name }}.conf'
        #)

    #def pre_make_package(self, context, **options):
    #    """ Callback called after package directory has been created
    #       :options: are options passed to make_package (deploy)
    #    """
    #    with fabric.api.settings(warn_only=True):
    #        with fabric.api.lcd(self.local_manage_dir):
    #            fabric.api.local('./manage.py collectstatic --noinput --clear')
    #            fabric.api.local('./manage.py compilemessages')

    #def post_make_package(self, context, **options):
    #    """ Callback called after package directory has been created
    #       :options: are options passed to make_package (deploy)
    #    """
    #    self.log('nice to meet you post_make_package callback')

    #def get_context_data(self, **kwargs):
    #    """ Here you can add custom variables for processing package source code
    #    """
    #    return super(Deployment, self).get_context_data(**kwargs)
