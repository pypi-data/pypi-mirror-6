import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

from . import lib


logger = logging.getLogger(__name__)


@staff_member_required
def index(request):
    """
    Render page with some way of firing actions.

    """
    actions = lib.get_actions()

    return render(
        request,
        'django_actions/index.html',
        {
            'actions': actions
        }
    )


@staff_member_required
def do(request, action_name_slugified):
    """
    Perform specified action and then redirect to index page.

    """
    try:
        action = lib.get_action(action_name_slugified)
        logger.info('Running action "{}"...'.format(action.name))
        inputs = [request.POST[input_] for input_ in action.inputs]
        action.do(*inputs)
        logger.info('Finished running action "{}"'.format(action.name))
    except lib.ActionNotFound:
        logger.error('Action not found for slugified name "{}"'.format(action_name_slugified))

    return redirect('django_actions_index')
