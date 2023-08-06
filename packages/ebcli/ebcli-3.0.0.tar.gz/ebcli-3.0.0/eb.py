#!/usr/bin/python2.7
#!C:\Python27\python.exe

import airspeed
import argparse
import getpass
import inspect
import json
import os
import sys
import traceback

from api_client import ElasticBoxClient, UnexpectedQuantityException, CONFIG_PATH, DEFAULT_TOKEN_PATH

client = ElasticBoxClient()

ENVIRONMENT_NAME_PARAM = (
    ['-e', '--environment'],
    {'help': 'Environment Name', 'required': True}
)
APPLICATION_NAME_PARAM = (
    ['-a', '--application'],
    {'help': 'Application Name', 'required': True}
)
BINDINGS_PARAM = (
    ['-b', '--bindings'],
    {'help': 'Application Box Name', 'required': False}
)
BOX_NAME_PARAM = (
    ['-b', '--box'],
    {'help': 'Application Box Name', 'required': True}
)
SCRIPT_NAME_PARAM = (
    ['-s', '--script-name'],
    {'help': 'Event script name', 'required': True}
)
PACKAGE_PARAM = (
    ['-p', '--package'],
    {'help': 'Package path', 'required': True}
)
FILE_PARAM = (
    ['file'],
    {'help': 'Path to file',
     'nargs': '?',
     'type': argparse.FileType('rb')}
)
OUTPUT_FILE_PARAM = (
    ['-o', '--output-file'],
    {'help': 'Path to output file',
     'type': argparse.FileType('wb'),
     'required': False,
     'dest': 'output'}
)
INPUT_FILE_PARAM = (
    ['-i', '--input-file'],
    {'help': 'Input file', 'required': True}
)
INSTANCE_NAME_PARAM = (
    ['-i', '--instance'],
    {'help': 'Instance Name', 'required': True}
)

WORKSPACE_PARAM = (
    ['-w', '--workspace'],
    {'help': 'Workspace', 'required': True}
)


# pylint: disable=R0903
class _BaseCommand(object):
    """Base class for all eb.py commands."""

    def __init__(self, args):
        self.args = args

    def _print(self, json_obj):
        """Tries to print the given object as JSON."""
        if not json_obj:
            return
        try:
            print json.dumps(json_obj, indent=4)
        except ValueError:
            print json_obj


class LoginCommand(_BaseCommand):
    def login(self):
        if not self.args.password:
            self.args.password = getpass.getpass('Password: ')

        client.log_in(self.args.url, self.args.user, self.args.password)
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)

        client.write_token_to_file(token_file_path=self.args.token_file)
        print 'Login successful, token saved on {}'.format(self.args.token_file)

    @staticmethod
    def parser(subparsers):
        parser_login = subparsers.add_parser('login', help='Log in to ElasticBox and save the token')

        parser_login.add_argument('-u', required=True, dest='user', help='ElasticBox user name')
        parser_login.add_argument('-p', required=False, dest='password', help='ElasticBox password')
        parser_login.add_argument('-d',
                                  dest='url',
                                  default='https://production.elasticbox.com',
                                  help='URL of the eb production instance')
        parser_login.add_argument('-f', '--token_file', default=DEFAULT_TOKEN_PATH)

        parser_login.set_defaults(func=_run_command)


class InstanceCommand(_BaseCommand):
    def list(self):
        self._print(client.instances.get_all())

    def get(self):
        self._print(client.instances.get_by_environment_and_box(
            self.args.workspace, self.args.environment, self.args.instance))

    def delete(self):
        instance = client.instances.get_by_environment_and_box(
            self.args.workspace, self.args.environment, self.args.instance)
        client.instances.delete(instance['id'])

    def start(self):
        instance = client.instances.get_by_environment_and_box(
            self.args.workspace, self.args.environment, self.args.instance)
        client.instances.start(instance['id'])

    def stop(self):
        instance = client.instances.get_by_environment_and_box(
            self.args.workspace, self.args.environment, self.args.instance)
        client.instances.stop(instance['id'])

    def reconfigure(self):
        instance = client.instances.get_by_environment_and_box(
            self.args.workspace, self.args.environment, self.args.instance)
        client.instances.reconfigure(instance['id'])

    def config(self):
        try:
            instance = client.workspaces.get_instance_by_environment(self.args.workspace, self.args.environment,
                                                                     self.args.instance)
        except UnexpectedQuantityException:
            print 'Unable to find an instance with application name {} and environment {} in the workspace {}'\
                  .format(self.args.instance, self.args.environment, self.args.workspace)
            return

        environment = client.instances._make_environment(instance)

        input_stream = sys.stdin if self.args.file is None else self.args.file
        output_stream = sys.stdout if self.args.output is None else self.args.output
        template = airspeed.Template(input_stream.read())
        template.merge_to(environment, output_stream)

    @staticmethod
    def parser(subparsers):
        parser_instance = subparsers.add_parser('instance', help='Manage application instances (list, start, stop)')
        instance_subparser = parser_instance.add_subparsers(title='Instance actions', dest='action')

        _subparser(instance_subparser, 'list', [], help_text='List of existing instances')
        _subparser(instance_subparser,
                   'get',
                   [ENVIRONMENT_NAME_PARAM, INSTANCE_NAME_PARAM],
                   help_text='Show given instance')
        _subparser(instance_subparser,
                   'delete',
                   [ENVIRONMENT_NAME_PARAM, INSTANCE_NAME_PARAM],
                   help_text='Deletes given instance')
        _subparser(instance_subparser,
                   'reconfigure',
                   [ENVIRONMENT_NAME_PARAM, INSTANCE_NAME_PARAM],
                   help_text='Reconfigure given instance')
        _subparser(instance_subparser,
                   'config',
                   [INSTANCE_NAME_PARAM, ENVIRONMENT_NAME_PARAM, WORKSPACE_PARAM,
                       BINDINGS_PARAM, FILE_PARAM, OUTPUT_FILE_PARAM],
                   help_text='Configuration file of given instance')


class WorkspaceCommand(_BaseCommand):

    def get_instance(self):
        self._print(client.workspaces.get_instance_by_environment(
            self.args.workspace, self.args.environment, self.args.instance))

    @staticmethod
    def parser(subparsers):
        parser_workspace = subparsers.add_parser('workspace', help='Manage workspaces')
        workspace_subparser = parser_workspace.add_subparsers(title='Workspace actions', dest='action')

        _subparser(workspace_subparser,
                   'get_instance',
                   [ENVIRONMENT_NAME_PARAM, INSTANCE_NAME_PARAM, WORKSPACE_PARAM],
                   help_text='Show given instance')


class ApplicationCommand(_BaseCommand):
    def list(self):
        self._print(client.applications.get_all())

    def boxes(self):
        self._print(client.applications.get_by_name(self.args.application)['boxes'])

    def push(self):
        application_id = client.applications.get_by_name(self.args.application)['id']
        box_id = client.applications.get_box_by_name(application_id, self.args.box)['id']
        self._print(client.applications.upload_box_package(application_id, box_id, self.args.package))

    @staticmethod
    def parser(subparsers):
        parser_app = subparsers.add_parser('application', help='Manage applications (list, boxes, push)')
        app_subparser = parser_app.add_subparsers(title='Application actions', dest='action')

        _subparser(app_subparser, 'list', [], help_text='Retrieves list of applications')
        _subparser(app_subparser, 'boxes', [APPLICATION_NAME_PARAM], help_text='Retrieves list of application boxes')
        _subparser(app_subparser,
                   'push',
                   [APPLICATION_NAME_PARAM, BOX_NAME_PARAM, PACKAGE_PARAM],
                   help_text='Uploads package to given box ID')


class EndpointsCommand(_BaseCommand):
    def get(self):
        instance = client.instances.get_by_environment_and_box(self.args.workspace, self.args.environment,
                                                               self.args.instance)
        if instance is None:
            message = 'Cannot find endpoints for workspace {0} and environment {1} and instance {2}'.format(
                self.args.workspace,
                self.args.environment,
                self.args.instance)
            raise Exception(message)

        self._print(dict(('{} {}'.format(box['name'], box['id']), box['endpoints'])
                         for box in instance['boxes']))

    @staticmethod
    def parser(subparsers):
        parser_endpoints = subparsers.add_parser('endpoints', help='Show instance endpoints')
        endpoint_subparser = parser_endpoints.add_subparsers(title='Endpoints actions', dest='action')

        _subparser(endpoint_subparser,
                   'get',
                   [ENVIRONMENT_NAME_PARAM, APPLICATION_NAME_PARAM],
                   help_text='Show given endpoints')


class VariablesCommand(_BaseCommand):
    def get(self):
        instance = client.instances.get_by_environment_and_box(self.args.workspace, self.args.environment,
                                                               self.args.instance)
        if instance is None:
            message = 'Cannot find variables for workspace {0} and environment {1} and instance {2}'.format(
                self.args.workspace,
                self.args.environment,
                self.args.instance)
            raise Exception(message)

        self._print(dict(('{} {}'.format(box['name'], box['id']), box['variables'])
                         for box in instance['boxes']))

    @staticmethod
    def parser(subparsers):
        parser_variables = subparsers.add_parser('variables', help='Show instance variables')
        variable_subparser = parser_variables.add_subparsers(title='Variables actions', dest='action')

        _subparser(variable_subparser,
                   'get',
                   [ENVIRONMENT_NAME_PARAM, APPLICATION_NAME_PARAM],
                   help_text='Show given variables')


class BoxesCommand(_BaseCommand):
    def list(self):
        self._print(client.boxes.get_all())

    def get(self):
        self._print(client.boxes.get_by_name(self.args.box))

    def create(self):
        self._print(client.boxes.create_from_json(self.args.input_file))

    def delete(self):
        self._print(client.boxes.delete_by_name(self.args.box))

    def script(self):
        self._print(client.boxes.upload_box_script(self.args.box, self.args.script_name, self.args.input_file))

    def dependency(self):
        self._print(client.boxes.upload_box_dependency(self.args.box, self.args.input_file))

    @staticmethod
    def parser(subparsers):
        parser_instance = subparsers.add_parser('boxes', help='Manage boxes instances (list, create, delete)')
        box_subparser = parser_instance.add_subparsers(title='Boxes actions', dest='action')

        _subparser(box_subparser, 'list', [], help_text='List of existing boxes')
        _subparser(box_subparser,
                   'get',
                   [BOX_NAME_PARAM],
                   help_text='Get given box')
        _subparser(box_subparser,
                   'create',
                   [INPUT_FILE_PARAM],
                   help_text='Create box from json definition')
        _subparser(box_subparser,
                   'delete',
                   [BOX_NAME_PARAM],
                   help_text='Delete given box')
        _subparser(box_subparser,
                   'script',
                   [BOX_NAME_PARAM, SCRIPT_NAME_PARAM, INPUT_FILE_PARAM],
                   help_text='Upload script to given box')
        _subparser(box_subparser,
                   'dependency',
                   [BOX_NAME_PARAM, INPUT_FILE_PARAM],
                   help_text='Upload script to given box')


def _run_command(args):
    if args.command != 'login':
        client.read_token_from_file(DEFAULT_TOKEN_PATH)

    class_name = args.command[0].upper() + args.command[1:] + 'Command'
    command = globals()[class_name](args)
    action = None
    if not hasattr(args, 'action'):
        action = args.command
    else:
        action = args.action
    getattr(command, action)()


def _subparser(subparser, action, arguments, help_text):
    parser = subparser.add_parser(action, help=help_text)
    parser.set_defaults(func=_run_command)
    for arg in arguments:
        parser.add_argument(*arg[0], **arg[1])


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='ElasticBox command line tool',
                                     epilog="See 'eb.py command --help' for more information on a specific command")

    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # Register the subparser for every _BaseCommand subclass
    for name, value in globals().items():
        if inspect.isclass(value) and issubclass(value, _BaseCommand):
            if name != '_BaseCommand':
                value.parser(subparsers)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    try:
        parse_command_line(sys.argv[1:])
    except:
        traceback.print_exc()
        sys.exit(1)
