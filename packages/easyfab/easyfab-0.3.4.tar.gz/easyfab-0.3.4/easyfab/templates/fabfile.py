"""
Universal deployment file based on fabric generated at {{ datetime }}
"""

import easyfab as ef
import fabric.api
from fabric.colors import green, red, magenta
import traceback
import unipath
import inspect

PROJECT_DIR = unipath.Path(__file__).parent


@fabric.api.task
def use(deployment):
    # set deployment
    try:
        ef.set_deployment(PROJECT_DIR, deployment)
    except ef.MissingDeploymentError:
        raise
        return fabric.api.abort("Deployment %s does not exist" % deployment)


@fabric.api.task
@ef.ensure_use_deployment
def easyfab(name, *args, **kwargs):
    deployment = fabric.api.env['__deployment']

    if name == 'list_commands':
        print green("Available easyfab commands:")
        for command in ef.list_commands(deployment):
            print red(command.__name__)
            if command.__doc__:
                print "\t" + command.__doc__.strip()
            argspec = inspect.getargspec(command)
            if argspec.args:
                print magenta('args:' + str(argspec.args))
        return

    func = getattr(deployment, name, None)
    if not func or not callable(func):
        fabric.api.abort("easyfab command `%s` not found on deployment %s" % (name, inspect.getfile(deployment.__class__)))

    if ef.is_easyfab_task(func):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print traceback.format_exc()
            fabric.api.abort("command %s raised exception %s" % (name, e))
    else:
        fabric.api.abort("command %s is not an easyfab task" % name)
