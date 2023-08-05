import importlib

from django.conf import settings
from django.utils.text import slugify

from funcy import memoize, decorator


class Action(object):
    """
    """
    def __init__(self, name, function, inputs):
        self.name = unicode(name)
        self.name_slugified = slugify(self.name)
        self.function = function
        self.inputs = inputs

    def do(self, *args):
        self.function(*args)


@decorator
def action(call, name, *inputs):
    """
    """
    # import debug
    return Action(name, call, inputs)


class ActionNotFound(Exception):
    """
    """
    pass


def import_from_actions_path():
        module = importlib.import_module(settings.ACTIONS_PATH)
        module_attributes = (getattr(module, attr_) for attr_ in dir(module))

        for attr in module_attributes:

            try:
                candidate = attr()
            except TypeError:
                continue

            if isinstance(candidate, Action):
                yield candidate

        # function = getattr(module)

        # if function:
        #     yield (function_name, function)


@memoize
def get_actions():
    return [a for a in import_from_actions_path()]


@memoize
def get_actions_by_name_slugified():
    return {act.name_slugified: act for act in get_actions()}


def get_action(name):
    actions = get_actions_by_name_slugified()
    try:
        return actions[name]
    except KeyError:
        raise ActionNotFound
