import inspect

import internetarchive.tasks



def load_plugins():
    modules = inspect.getmembers(internetarchive.tasks, inspect.ismodule)
    for name, value in modules:
        print name
        module = 'internetarchive.tasks.{m}'.format(m=name)
        functions = inspect.getmembers(module, inspect.isfunction)
    #plugin_names = {
    #    'upload': 'internetarchive.tasks.upload',
    #    'download': 'internetarchive.tasks.download',
    #    'get_item': 'internetarchive.tasks.get_item',
    #}
    #tasks = _import_plugins(plugin_names)
    #for name, task in tasks.items():
    #    setattr(object, name, task.main)
    #return object


def _import_plugins(plugin_names, plugins={}):
    for name, path in plugin_names.items():
        package, module = path.rsplit('.', 1)
        module = __import__(path, fromlist=[module])
        plugins[name] = module
    return plugins

load_plugins()
