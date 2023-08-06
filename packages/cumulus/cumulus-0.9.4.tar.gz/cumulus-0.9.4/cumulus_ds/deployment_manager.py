""" The deployment manager handles all deployments of CloudFormation stacks """
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

import boto

import cumulus_ds
from cumulus_ds import connection_handler
from cumulus_ds import terminal_size
from cumulus_ds.exceptions import (
    InvalidTemplateException,
    HookExecutionException)

LOGGER = logging.getLogger(__name__)

TERMINAL_WIDTH, _ = terminal_size.get_terminal_size()


def deploy():
    """ Ensure stack is up and running (create or update it) """
    # Run pre-deploy-hook
    _pre_deploy_hook()

    stacks = cumulus_ds.config.get_stacks()

    if not stacks:
        LOGGER.warning('No stacks configured, nothing to deploy')
        return

    for stack in stacks:
        _ensure_stack(
            stack,
            cumulus_ds.config.get_stack_template(stack),
            disable_rollback=cumulus_ds.config.get_stack_disable_rollback(
                stack),
            parameters=cumulus_ds.config.get_stack_parameters(stack),
            timeout_in_minutes=cumulus_ds.config.get_stack_timeout_in_minutes(
                stack),
            tags=cumulus_ds.config.get_stack_tags(stack))

    # Run post-deploy-hook
    _post_deploy_hook()


def list_events():
    """ List events """
    try:
        con = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack_name in cumulus_ds.config.get_stacks():
        stack = _get_stack_by_name(stack_name)

        if not stack:
            break

        _print_event_log_title()

        written_events = []
        for event in reversed(con.describe_stack_events(stack.stack_id)):
            if event.event_id not in written_events:
                written_events.append(event.event_id)
                _print_event_log_event(event)


def list_stacks():
    """ List stacks and their statuses """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    cf_stacks = connection.list_stacks()

    for stack in cumulus_ds.config.get_stacks():
        stack_found = False
        for cf_stack in cf_stacks:
            if stack == cf_stack.stack_name:
                stack_found = True

        if stack_found:
            print('{:<30}{}'.format(stack, cf_stack.stack_status))
        else:
            print('{:<30}{}'.format(stack, 'NOT_RUNNING'))


def undeploy(force=False):
    """ Undeploy an environment

    :type force: bool
    :param force: Skip the safety question
    """
    message = (
        'This will DELETE all stacks in the environment. '
        'This action cannot be undone. '
        'Are you sure you want to do continue? [N/y] ')

    choice = 'yes'
    if not force:
        choice = raw_input(message).lower()
        if choice not in ['yes', 'y']:
            print('Skipping undeployment.')
            return None

    stacks = cumulus_ds.config.get_stacks()
    stacks.reverse()

    if not stacks:
        LOGGER.warning('No stacks to undeploy.')
        return None

    for stack in stacks:
        _delete_stack(stack)


def validate_templates():
    """ Validate the template """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in cumulus_ds.config.get_stacks():
        template = cumulus_ds.config.get_stack_template(stack)

        result = connection.validate_template(
            _get_json_from_template(template))
        if result:
            LOGGER.info('Template {} is valid!'.format(template))


def _ensure_stack(
        stack_name, template,
        disable_rollback=False, parameters=[],
        timeout_in_minutes=None, tags=None):
    """ Ensure stack is up and running (create or update it)

    :type stack_name: str
    :param stack_name: Stack name
    :type template: str
    :param template: Template path to use
    :type disable_rollback: bool
    :param disable_rollback: Should rollbacks be disabled?
    :type parameters: list
    :param parameters: List of tuples with CF parameters
    :type timeout_in_minutes: int or None
    :param timeout_in_minutes:
        Consider the stack FAILED if creation takes more than x minutes
    :type tags: dict or None
    :param tags: Dictionary of keys and values to use as CloudFormation tags
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    LOGGER.info('Ensuring stack {} with template {}'.format(
        stack_name, template))

    cumulus_parameters = [
        (
            'CumulusBundleBucket',
            cumulus_ds.config.get_environment_option('bucket')
        ),
        (
            'CumulusEnvironment',
            cumulus_ds.config.get_environment()
        ),
        (
            'CumulusVersion',
            cumulus_ds.config.get_environment_option('version')
        )
    ]

    if timeout_in_minutes:
        LOGGER.debug('Will time out stack creation after {:d} minutes'.format(
            timeout_in_minutes))

    for parameter in cumulus_parameters + parameters:
        LOGGER.debug(
            'Adding parameter "{}" with value "{}" to CF template'.format(
                parameter[0], parameter[1]))

    try:
        if _stack_exists(stack_name):
            LOGGER.debug('Updating existing stack to version {}'.format(
                cumulus_ds.config.get_environment_option('version')))

            if template[0:4] == 'http':
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                connection.update_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)

            _wait_for_stack_complete(stack_name, filter_type='UPDATE')
        else:
            LOGGER.debug('Creating new stack with version {}'.format(
                cumulus_ds.config.get_environment_option('version')))
            if template[0:4] == 'http':
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_url=template,
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)
            else:
                connection.create_stack(
                    stack_name,
                    parameters=cumulus_parameters + parameters,
                    template_body=_get_json_from_template(template),
                    disable_rollback=disable_rollback,
                    capabilities=['CAPABILITY_IAM'],
                    timeout_in_minutes=timeout_in_minutes,
                    tags=tags)

            _wait_for_stack_complete(stack_name, filter_type='CREATE')

    except ValueError as error:
        raise InvalidTemplateException(
            'Malformatted template: {}'.format(error))
    except boto.exception.BotoServerError as error:
        code = eval(error.error_message)['Error']['Code']
        message = eval(error.error_message)['Error']['Message']

        if code == 'ValidationError':
            if message == 'No updates are to be performed.':
                # Do not raise this exception if it is due to lack of updates
                # We do not want to fail any other stack updates after this
                # stack
                LOGGER.warning(
                    'No CloudFormation updates are to be '
                    'performed for {}'.format(stack_name))
                return

        LOGGER.error('Boto exception {}: {}'.format(code, message))
        return


def _delete_stack(stack):
    """ Delete an existing stack

    :type stack: str
    :param stack: Stack name
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    LOGGER.info('Deleting stack {}'.format(stack))
    connection.delete_stack(stack)
    _wait_for_stack_complete(stack, filter_type='DELETE')


def _get_json_from_template(template):
    """ Returns a JSON string given a template file path

    :type template: str
    :param template: Template path to use
    :returns: JSON object
    """
    template_path = ospath.expandvars(ospath.expanduser(template))
    LOGGER.debug('Parsing template file {}'.format(template_path))

    file_handle = open(template_path)
    json_data = json.dumps(json.loads(file_handle.read()))
    file_handle.close()

    return json_data


def _get_stack_by_name(stack_name):
    """ Returns a stack given its name

    :type stack_name: str
    :param stack_name: Stack name
    :returns: stack or None
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in connection.list_stacks():
        if (stack.stack_status != 'DELETE_COMPLETE' and
                stack.stack_name == stack_name):
            return stack

    return None


def _pre_deploy_hook():
    """ Execute a pre-deploy-hook """
    command = cumulus_ds.config.get_pre_deploy_hook()

    if not command:
        return None

    LOGGER.info('Running pre-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The pre-deploy-hook returned a non-zero exit code: {}'.format(
                error))


def _print_event_log_event(event):
    """ Print event log row to stdout

    :type event: event object
    :param event: CloudFormation event object
    """
    # Colorize status
    event_status = event.resource_status.split('_')
    if event_status[len(event_status) - 1] == 'COMPLETE':
        # Green text
        status = '\033[92m' + event.resource_status + '\033[0m'
    elif event_status[len(event_status) - 1] == 'PROGRESS':
        # Blue text
        status = '\033[94m' + event.resource_status + '\033[0m'
    elif event_status[len(event_status) - 1] == 'FAILED':
        # Red text
        status = '\033[91m' + event.resource_status + '\033[0m'
    else:
        status = event.resource_status

    row = '{timestamp:<19}'.format(
        timestamp=datetime.strftime(event.timestamp, '%Y-%m-%d %H:%M:%S'))
    row += ' | {type:<45}'.format(type=event.resource_type)
    row += ' | {logical_id:<42}'.format(logical_id=event.logical_resource_id)

    if TERMINAL_WIDTH >= 190:
        if event.resource_status_reason:
            reason = event.resource_status_reason
        else:
            reason = ''

        row += ' | {reason:<36}'.format(reason=reason)

    row += ' | {status:<33}'.format(status=status.replace('_', ' ').lower())

    print(row)


def _print_event_log_separator():
    """ Print separator line for the event log """
    row = '--------------------'  # Timestamp
    row += '+-----------------------------------------------'  # Resource type
    row += '+--------------------------------------------'  # Logical ID

    if TERMINAL_WIDTH >= 190:
        row += '+--------------------------------------'  # Reason

    row += '+--------------------------------'  # Status

    print(row)


def _print_event_log_title():
    """ Print event log title row on stdout """
    _print_event_log_separator()

    row = '{timestamp:<19}'.format(timestamp='Timestamp')
    row += ' | {type:<45}'.format(type='Resource type')
    row += ' | {logical_id:<42}'.format(logical_id='Logical ID')
    if TERMINAL_WIDTH >= 190:
        row += ' | {reason:<36}'.format(reason='Reason')
    row += ' | {status:<25}'.format(status='Status')

    print(row)

    _print_event_log_separator()


def _post_deploy_hook():
    """ Execute a post-deploy-hook """
    command = cumulus_ds.config.get_post_deploy_hook()

    if not command:
        return None

    LOGGER.info('Running post-deploy-hook command: "{}"'.format(command))
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, error:
        raise HookExecutionException(
            'The post-deploy-hook returned a non-zero exit code: {}'.format(
                error))


def _stack_exists(stack_name):
    """ Check if a stack exists

    :type stack_name: str
    :param stack_name: Stack name
    :returns: bool
    """
    try:
        connection = connection_handler.connect_cloudformation()
    except Exception:
        raise

    for stack in connection.list_stacks():
        if (stack.stack_status != 'DELETE_COMPLETE' and
                stack.stack_name == stack_name):
            return True

    return False


def _wait_for_stack_complete(stack_name, check_interval=5, filter_type=None):
    """ Wait until the stack create/update has been completed

    :type stack_name: str
    :param stack_name: Stack name
    :type check_interval: int
    :param check_interval: Seconds between each console update
    :type filter_type: str
    :param filter_type: Filter events by type. Supported values are None,
        CREATE, DELETE, UPDATE. Rollback events are always shown.
    """
    start_time = datetime.utcnow() - timedelta(0, 10)
    complete = False
    complete_statuses = [
        'CREATE_FAILED',
        'CREATE_COMPLETE',
        'ROLLBACK_FAILED',
        'ROLLBACK_COMPLETE',
        'DELETE_FAILED',
        'DELETE_COMPLETE',
        'UPDATE_COMPLETE',
        'UPDATE_ROLLBACK_FAILED',
        'UPDATE_ROLLBACK_COMPLETE'
    ]
    try:
        con = connection_handler.connect_cloudformation()
    except Exception:
        raise

    written_events = []

    while not complete:
        stack = _get_stack_by_name(stack_name)
        if not stack:
            _print_event_log_separator()
            break

        if not written_events:
            _print_event_log_title()

        for event in reversed(con.describe_stack_events(stack.stack_id)):
            # Don't print written events
            if event.event_id in written_events:
                continue

            # Don't print old events
            if event.timestamp < start_time:
                continue

            written_events.append(event.event_id)

            event_type, _ = event.resource_status.split('_', 1)
            log = False
            if not filter_type:
                log = True
            elif (filter_type == 'CREATE'
                    and event_type in ['CREATE', 'ROLLBACK']):
                log = True
            elif (filter_type == 'DELETE'
                    and event_type in ['DELETE', 'ROLLBACK']):
                log = True
            elif (filter_type == 'UPDATE'
                    and event_type in ['UPDATE', 'ROLLBACK']):
                log = True

            if not log:
                continue

            _print_event_log_event(event)

        if stack.stack_status in complete_statuses:
            _print_event_log_separator()
            LOGGER.info('Stack {} - Stack completed with status {}'.format(
                stack.stack_name,
                stack.stack_status))
            complete = True

        time.sleep(check_interval)
