'''
ElasticBox Confidential
Copyright (c) 2013 All Right Reserved, ElasticBox Inc.

NOTICE:  All information contained herein is, and remains the property
of ElasticBox. The intellectual and technical concepts contained herein are
proprietary and may be covered by U.S. and Foreign Patents, patents in process,
and are protected by trade secret or copyright law. Dissemination of this
information or reproduction of this material is strictly forbidden unless prior
written permission is obtained from ElasticBox
'''

import argparse
import json
import httplib
import os
import requests
import stat
import urlparse
import uuid
from mimetypes import types_map

from common import resources
from common.collections import AttrDict

REQUESTS_TIMEOUT_SECONDS = 10

CONFIG_PATH = os.path.expanduser('~/.elasticbox')
DEFAULT_TOKEN_PATH = os.path.join(CONFIG_PATH, 'api_client_token')


# These are URL templates that are used to reach different controllers in the web services.
# Instances
START_INSTANCE_TEMPLATE = '{instance_id}/poweron'
STOP_INSTANCE_TEMPLATE = '{instance_id}/shutdown'
RECONFIGURE_INSTANCE_TEMPLATE = '{instance_id}/reconfigure'

# Applications
BOXES_TEMPLATE = '{application_id}/boxes'
UPLOAD_BOX_BLOB_TEMPLATE = 'services/blobs/upload/{0}'
INDIVIDUAL_BOX_TEMPLATE = '{application_id}/boxes/{box_id}'

# Providers
SYNC_PROVIDER_TEMPLATE = '{provider_id}/sync'
IMAGES_TEMPLATE = '{provider_id}/images'

# Workspaces
INSTANCES_TEMPLATE = '{workspace_id}/instances'


class UnexpectedQuantityException(Exception):
    pass


class MalformedTokenFileException(Exception):
    pass


class RESTBase(object):
    # This is the base client; it provides basic CRUD operations. More specific REST API clients
    # (e.g. InstancesCommands and ApplicationsCommands below) extend this class to provide more
    # specific commands; e.g. InstancesCommands also has calls to start and stop instances.
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url

    def _add_token(self, payload):
        # We have to add the ElasticBox token to each http request
        if 'headers' not in payload:
            payload['headers'] = dict()
        payload['verify'] = False
        payload['headers']['ElasticBox-Token'] = self.token
        payload['headers']['content-type'] = 'application/json'
        return payload

    # pylint: disable=W0142
    def _http_get(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        response = requests.get(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    # pylint: disable=W0142
    def _http_post(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        response = requests.post(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    # pylint: disable=W0142
    def _http_put(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        response = requests.put(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    # pylint: disable=W0142
    def _http_delete(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        response = requests.delete(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    def _upload_file(self, file_path):
        if self.base_url.startswith('https'):
            host_address = 'https://{}'.format(urlparse.urlparse(self.base_url).hostname)
        elif self.base_url.startswith('http'):
            host_address = 'http://{}'.format(urlparse.urlparse(self.base_url).hostname)

        filename = file_path.split('/')[-1]
        absolute_url = urlparse.urljoin(host_address, UPLOAD_BOX_BLOB_TEMPLATE.format(filename))

        _, extension = os.path.splitext(file_path)
        content_type = 'application/octet-stream'

        if extension in types_map:
            content_type = types_map[extension]

        headers = {'Content-Type': content_type}

        with open(file_path, 'r') as body:
            return self._http_post(absolute_url, headers=headers, data=body)

    def _create(self, creation_dict):
        json_encoded = creation_dict if isinstance(creation_dict, str) else json.dumps(creation_dict)
        return self._http_post(self.base_url, json_encoded)

    def create(self, creation_dict):
        return self._create(creation_dict).json(object_hook=AttrDict)

    def _get_all(self):
        return self._http_get(self.base_url)

    def get_all(self):
        return self._get_all().json(object_hook=AttrDict)

    def _get_by_id(self, resource_id):
        return self._http_get(urlparse.urljoin(self.base_url, str(resource_id)))

    def get_by_id(self, resource_id):
        return self._get_by_id(resource_id).json(object_hook=AttrDict)

    def _get_by_name(self, resource_name):
        all_resources = self.get_all()
        matching_instance = [obj for obj in all_resources if obj['name'] == resource_name]
        if len(matching_instance) != 1:
            raise UnexpectedQuantityException(
                'A total of {} resources with name {} were found'.format(len(matching_instance), resource_name))
        resource = self._get_by_id(matching_instance[0]['id'])
        return resource

    def get_by_name(self, resource_name):
        return self._get_by_name(resource_name).json(object_hook=AttrDict)

    def _update(self, resource_id, update_dict):
        json_encoded = update_dict if isinstance(update_dict, str) else json.dumps(update_dict)
        return self._http_put(urlparse.urljoin(self.base_url, str(resource_id)), data=json_encoded)

    def update(self, resource_id, update_dict):
        return self._update(resource_id, update_dict).json(object_hook=AttrDict)

    def _delete(self, resource_id):
        return self._http_delete(urlparse.urljoin(self.base_url, str(resource_id)))

    def delete(self, resource_id):
        self._delete(resource_id)

    def _delete_by_name(self, resource_name):
        resource = self._get_by_name(resource_name).json(object_hook=AttrDict)
        self._delete(resource['id'])

    def delete_by_name(self, resource_name):
        self._delete_by_name(resource_name)


class InstancesCommands(RESTBase):
    # Classes like this one (InstancesCommands, ApplicationsCommands, etc.) have all the commands from RESTBase
    # along with more specialist ones. E.g. to stop an instance with id instance_id, one could do
    # client.instances.stop(instance_id)
    def __init__(self, token, host_address, controller_route):
        super(InstancesCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def _start(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               START_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def start(self, instance_id):
        return self._start(instance_id).json(object_hook=AttrDict)

    def _stop(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               STOP_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def stop(self, instance_id):
        self._stop(instance_id)

    def _reconfigure(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               RECONFIGURE_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def reconfigure(self, instance_id):
        self._reconfigure(instance_id)

    def _delete(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': resources.DELETE_INSTANCE_REST_TYPE})

    def delete(self, instance_id):
        self._delete(instance_id)

    def _terminate(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': resources.TERMINATE_INSTANCE_REST_TYPE})

    def terminate(self, instance_id):
        self._terminate(instance_id)

    def _force_terminate(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': resources.FORCE_TERMINATE_INSTANCE_REST_TYPE})

    def force_terminate(self, instance_id):
        self._force_terminate(instance_id)

    def _launch(self, application_id, environment, resources_list):
        payload = {'application_id': application_id,
                   'environment': environment,
                   'resources': resources_list}

        json_encoded = json.dumps(payload)
        return self._http_post(self.base_url, data=json_encoded)

    def launch(self, application_id, environment, resources_list):
        return self._launch(
            application_id, environment, resources_list).json(object_hook=AttrDict)

    def get_box_logs(self, instance_id):
        instance = self.get_by_id(instance_id)

        if self.base_url.startswith('https'):
            host_address = 'https://{}'.format(urlparse.urlparse(self.base_url).hostname)
        elif self.base_url.startswith('http'):
            host_address = 'http://{}'.format(urlparse.urlparse(self.base_url).hostname)
        else:
            raise Exception('Unable to extract the host address from the base url {}'.format(self.base_url))

        box_log_relative_urls = dict((box['id'], box['box_instance_logs'][0]['log_urls']) for box in instance['boxes'])
        box_logs = dict()
        for box_id, log_url_list in box_log_relative_urls.iteritems():
            these_logs = []
            for url in log_url_list:
                these_logs.append(self._http_get(urlparse.urljoin(host_address, url)).text)
            box_logs[box_id] = ''.join(these_logs)
        return box_logs

    def get_by_environment_and_box(self, workspace_name, environment_name, box_name):
        all_resources = self.get_all()
        environment_matches = [obj for obj in all_resources if obj['environment'] == environment_name]
        matching_instance = [obj for obj in environment_matches if obj['name'] == box_name]
        if len(matching_instance) == 0:
            return None
        elif len(matching_instance) > 1:
            raise Exception(
                'A total of {} instances with environment {} in the workspace {} were found'
                .format(len(matching_instance), environment_name, workspace_name))

        return self._get_by_id(matching_instance[0]['id']).json(object_hook=AttrDict)

    def get_box_bindings(self, instance_id, box_id):
        instance = self.get_by_id(instance_id)
        matching_boxes = [box for box in instance['boxes'] if box['id'] == box_id]
        if len(matching_boxes) == 0:
            raise Exception('No box instances with id {} were found'.format(box_id))
        box = matching_boxes[0]

        bindings = box['box_instance_bindings']
        for binding in bindings:
            binding_box_name = binding['box_name']
            matching_box_instances = [b for b in instance['boxes'] if b['name'] == binding_box_name]
            if len(matching_box_instances) == 0:
                raise UnexpectedQuantityException('Unable to find a box instance with name {} in the instance {}'
                                                  .format(binding_box_name, instance_id))
            box_fulfilling_binding = matching_box_instances[0]

            binding['endpoints'] = box_fulfilling_binding['endpoints']

        return bindings

    def get_box(self, instance_id, box_id):
        response = self._http_get(urlparse.urljoin(self.base_url, '{}/boxes/{}'.format(instance_id, box_id)))
        response.raise_for_status()
        return response.json(object_hook=AttrDict)

    def _make_environment(self, instance):
        return AttrDict(workspace=instance.workspace,
                        environment=instance.environment,
                        bindings=[],
                        variables=instance.variables)


class ApplicationsCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(ApplicationsCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def _convert_box_type(self, box, box_name):
        box['box_type_id'] = box['id']
        box['id'] = str(uuid.uuid4())

        del box['tags']
        if 'schema_version' in box:
            del box['schema_version']

        box['enable_remote_access'] = box['allow_enable_remote_access']
        del box['allow_enable_remote_access']
        box['box_package_destination_path'] = box['package_destination_path']
        del box['package_destination_path']
        box['box_install_script'] = box['install_script']
        del box['install_script']
        box['box_start_script'] = box['start_script']
        del box['start_script']

        box['box_type_name'] = box['name']
        if box_name is not None:
            box['name'] = box_name

        box['box_ports'] = box['box_type_ports']
        del box['box_type_ports']
        box['box_dependencies'] = box['box_type_dependencies']
        del box['box_type_dependencies']
        box['box_fields'] = box['box_type_fields']
        del box['box_type_fields']
        box['box_variables'] = box['box_type_variables']
        del box['box_type_variables']
        box['box_bindings'] = box['box_type_bindings']
        del box['box_type_bindings']

        return box

    def _add_box(self, application_id, box_type, box_name):
        application_box = self._convert_box_type(box_type, box_name)
        return self._http_post(urlparse.urljoin(self.base_url, BOXES_TEMPLATE.format(application_id=application_id)),
                               data=json.dumps(application_box))

    def add_box(self, application_id, box_type, box_name=None):
        return self._add_box(application_id, box_type, box_name)

    def _get_boxes(self, application_id):
        return self._http_get(urlparse.urljoin(self.base_url, BOXES_TEMPLATE.format(application_id=application_id)))

    def get_boxes(self, application_id):
        return self._get_boxes(application_id).json(object_hook=AttrDict)

    def get_box_by_name(self, application_id, box_name):
        all_boxes = self.get_boxes(application_id)
        matching_boxes = [box for box in all_boxes if box['name'] == box_name]
        if len(matching_boxes) != 1:
            raise UnexpectedQuantityException('A total of {} boxes with name {} were found'.format(len(matching_boxes),
                                                                                                   box_name))
        return matching_boxes[0]

    def _update_box(self, application_id, box_id, updated_box):
        json_encoded = updated_box if isinstance(updated_box, str) else json.dumps(updated_box)
        return self._http_put(urlparse.urljoin(self.base_url,
                                               INDIVIDUAL_BOX_TEMPLATE.format(
                                                   application_id=application_id, box_id=box_id)),
                              json_encoded)

    def update_box(self, application_id, box_id, updated_box):
        return self._update_box(application_id, box_id, updated_box).json(object_hook=AttrDict)

    def _upload_box_package(self, application_id, box_id, file_path):
        application = self.get_by_id(application_id)
        matching_boxes = [box for box in application['boxes'] if box['id'] == box_id]
        if len(matching_boxes) == 0:
            raise UnexpectedQuantityException('No boxes with id {} were found in application {}'
                                              .format(box_id, application_id))

        box = matching_boxes[0]
        if box['allow_user_package'] is False:
            raise Exception('Box {0} does not allow to upload dependencies'.format(box['name']))

        filename = file_path.split('/')[-1]
        dependency = self._upload_file(file_path).json(object_hook=AttrDict)

        dependency['destination_path'] = file_path.replace('/' + filename, '')
        for existing_dependency in box['box_dependencies']:
            if existing_dependency['destination_path'] == dependency['destination_path']:
                box['box_dependencies'].remove(existing_dependency)
                box['box_dependencies'].append(dependency)
                return self.update_box(application_id, box_id, box)

        box['box_dependencies'].append(dependency)
        return self.update_box(application_id, box_id, box)

    def upload_box_package(self, application_id, box_id, file_path):
        return self._upload_box_package(application_id, box_id, file_path)


class BoxesCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(BoxesCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def _create_from_json(self, json_definition):
        if json_definition.endswith('.json'):
            with open(json_definition, 'r') as box_file:
                new_box = json.load(box_file)
                existing_boxes = [box for box in self.get_all() if box['name'] == new_box['name']]
                if len(existing_boxes) > 0:
                    raise Exception('Box {0} already exists'.format(new_box['name']))

                for script_name in resources.SCRIPT_EVENTS:
                    if script_name in new_box:
                        uploaded_script = self._upload_file(new_box[script_name]).json(object_hook=AttrDict)
                        new_box[script_name] = AttrDict(uploaded_script, destination_path='scripts')

            return self._create(new_box)

    def create_from_json(self, json_definition):
        return self._create_from_json(json_definition).json(object_hook=AttrDict)

    def _upload_box_script(self, box_name, script_name, script_path):
        if script_name not in resources.SCRIPT_EVENTS:
            raise Exception('Script event {0} is currently not supported.'.format(script_name))

        box = self._get_by_name(box_name).json(object_hook=AttrDict)
        script = AttrDict(self._upload_file(script_path).json(object_hook=AttrDict), destination_path='scripts')
        box[script_name] = script
        return self._update(box['id'], box)

    def upload_box_script(self, box_name, script_name, script_path):
        return self._upload_box_script(box_name, script_name, script_path).json(object_hook=AttrDict)

    def _upload_box_dependency(self, box_name, file_path):
        box = self._get_by_name(box_name).json(object_hook=AttrDict)

        filename = file_path.split('/')[-1]
        dependency = self._upload_file(file_path).json(object_hook=AttrDict)

        dependency['destination_path'] = file_path.replace('/' + filename, '')
        for existing_dependency in box['box_type_dependencies']:
            if existing_dependency['destination_path'] == dependency['destination_path']:
                box['box_type_dependencies'].remove(existing_dependency)
                box['box_type_dependencies'].append(dependency)
                return self._update(box['id'], box)

        box['box_type_dependencies'].append(dependency)
        return self._update(box['id'], box)

    def upload_box_dependency(self, box_name, file_path):
        return self._upload_box_dependency(box_name, file_path).json(object_hook=AttrDict)


class ProvidersCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(ProvidersCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def _sync(self, provider_id):
        return self._http_put(urlparse.urljoin(self.base_url, SYNC_PROVIDER_TEMPLATE.format(provider_id=provider_id)))

    def sync(self, provider_id):
        return self._sync(provider_id).json(object_hook=AttrDict)

    def _add_image(self, provider_id, machine_image):
        return self._http_post(
            urlparse.urljoin(self.base_url, IMAGES_TEMPLATE.format(provider_id=provider_id)),
            data=machine_image)

    def add_image(self, provider_id, machine_image):
        return self._add_image(provider_id, machine_image).json(object_hook=AttrDict)

    def _get_images(self, provider_id):
        return self._http_get(urlparse.urljoin(self.base_url, IMAGES_TEMPLATE.format(provider_id=provider_id)))

    def get_images(self, provider_id):
        return self._get_images(provider_id).json(object_hook=AttrDict)


class UsersCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(UsersCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))


class ResourcesCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(ResourcesCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))


class CertificatesCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(CertificatesCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))


class WorkspacesCommands(RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(WorkspacesCommands, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def get_instance_by_environment(self, workspace, environment, instance_name):
        all_resources = self._http_get(
            urlparse.urljoin(
                self.base_url, INSTANCES_TEMPLATE.format(workspace_id=workspace))).json(object_hook=AttrDict)
        matching_instance = [
            obj for obj in all_resources if obj['name'] == instance_name and obj['environment'] == environment]
        if len(matching_instance) != 1:
            raise UnexpectedQuantityException(
                'A total of {} resources with name {} were found'.format(len(matching_instance), instance_name))
        resource = self._http_get(
            urlparse.urljoin(self.base_url, matching_instance[0]['uri'])).json(object_hook=AttrDict)
        return resource


class ElasticBoxClient(object):
    '''
Example usage:

    client = ElasticBoxClient()
    client.log_in('localhost', 'admin@elasticbox.com', 'elasticbox')

    # Demote all architects to engineers
    for user in client.users.get_all():
        if user['architect']:
            user['architect'] = False
            user['engineer'] = True
            client.users.update(user['id'], user)

    # Delete all instances
    for instance in client.instances.get_all():
        client.instances.delete(instance['id'])

    # Upload a package 'package_name' to box 'box_name' on application 'app_name':
    application= client.applications.get_by_name('app_name')
    box = client.applications.get_box_by_name(application['id'], 'box_name')
    client.applications.upload_box_package(application['id'], box['id'], 'package_name')

    # Sync all provider:
    for provider in client.providers.get_all():
        client.providers.sync(provider['id'])

    # Launch an instance. Notice that this is a huge pain because of the amount of info needed:
    application_id =  "674d4fac-23d7-4dc6-92d3-7d8f36da72bb"
    environment = "launch_it"
    resources = [{'provider_id': "5090b505-c536-4f86-b8ae-3ca20442dca5",
                  'box_id': "f68db3b8-c528-4ff1-93e1-d6caa263efc3",
                  'flavor_id': "73c2edf4-1f1a-4382-9124-474ee1b61607",
                  'instances': 1,
                  'location': "us-west-1",
                  'machine_image_id': "bc226ad7-4034-4388-bdb4-a85d105c667b"}]

    client.instances.launch(application_id, environment, resources)
'''

    def __init__(self):
        self.token = None
        self.host_address = None
        self.controller_routes = None
        # We actually read the routes to the web service controllers from the web services itself.
        # So we don't assume that the route to the instances controller is services/instances; instead
        # we query services/roots to tell us what all the other routes are.
        # You can see this in either read_token_from_file in log_in below.

    def read_token_from_file(self, token_file_path=DEFAULT_TOKEN_PATH):
        # The client needs a token to issue calls to the web services. You can either
        # read this token from a file (this method) or log in directly with a password
        # and username (the log_in method below).
        if not os.path.exists(token_file_path):
            self.raise_for_login()

        try:
            with open(token_file_path) as token_file:
                info = token_file.read().split(',')
                self.token = info[0]
                self.host_address = info[1]

            headers = {'X-AUTH-TOKEN': self.token, 'ElasticBox-Token': self.token}
            controller_routes_response = requests.get(
                '{}/services/roots'.format(self.host_address), headers=headers, verify=False)
            controller_routes_response.raise_for_status()
            if controller_routes_response.status_code in [httplib.FORBIDDEN, httplib.UNAUTHORIZED]:
                print 'Authenticating with token from file {} failed. Try logging in manually:'.format(token_file_path)
                email = raw_input('Email: ')
                password = raw_input('Password: ')
                self.log_in(self.host_address, email, password)
                self.write_token_to_file(token_file_path)
                headers = {'X-Auth-Token': self.token, 'ElasticBox-Token': self.token}
                controller_routes_response = requests.get(
                    '{}/services/roots'.format(self.host_address), headers=headers, verify=False)

            self.controller_routes = dict()
            for key, value in controller_routes_response.json(object_hook=AttrDict).items():
                self.controller_routes[str(key)] = '{}/'.format(value.strip('/'))
        except:
            raise MalformedTokenFileException("File {0} does not contain a valid token.".format(token_file_path))

    def write_token_to_file(self, token_file_path=DEFAULT_TOKEN_PATH):
        with open(token_file_path, 'w') as token_file:
            token_file.write('{},{}'.format(self.token, self.host_address))
        os.chmod(token_file_path, stat.S_IREAD | stat.S_IWRITE)

    def log_in(self, host_address, email, password):
        payload = dict(email=email, password=password, remember='on')
        if not (host_address.startswith('http://') or host_address.startswith('https://')):
            revised_address = 'http://{}'.format(host_address.strip('/'))
        else:
            revised_address = host_address

        response = requests.post(
            urlparse.urljoin(revised_address, '/services/security/token'),
            data=payload,
            verify=False)
        response.raise_for_status()
        token = str(response.text).strip('"')
        self.token = token
        self.host_address = revised_address

        headers = {'X-Auth-Token': self.token, 'ElasticBox-Token': self.token}
        raw_controller_info = requests.get(
            '{}/services/roots'.format(revised_address), headers=headers, verify=False).json(object_hook=AttrDict)

        self.controller_routes = dict()
        for key, value in raw_controller_info.items():
            self.controller_routes[str(key)] = '{}/'.format(value.strip('/'))

    def raise_for_login(self):
        if self.controller_routes is None:
            raise Exception('You need to log in before calling any functions')

    # These properties are here to enable easy access to the different parts of the client.
    # So if client is an instance of ElasticBoxClient, then client.applications will be an instance
    # of the ApplicationsCommands class. See the example usage at the top of this file.
    @property
    def instances(self):
        self.raise_for_login()
        return InstancesCommands(self.token, self.host_address, self.controller_routes['instances'])

    @property
    def workspaces(self):
        self.raise_for_login()
        return WorkspacesCommands(self.token, self.host_address, self.controller_routes['workspaces'])

    @property
    def applications(self):
        self.raise_for_login()
        return ApplicationsCommands(self.token, self.host_address, self.controller_routes['applications'])

    @property
    def boxes(self):
        self.raise_for_login()
        return BoxesCommands(self.token, self.host_address, self.controller_routes['boxes'])

    @property
    def providers(self):
        self.raise_for_login()
        return ProvidersCommands(self.token, self.host_address, self.controller_routes['providers'])

    @property
    def users(self):
        self.raise_for_login()
        return ProvidersCommands(self.token, self.host_address, self.controller_routes['users'])

    @property
    def resources(self):
        self.raise_for_login()
        return ResourcesCommands(self.token, self.host_address, self.controller_routes['resources'])

    @property
    def certificates(self):
        self.raise_for_login()
        return CertificatesCommands(self.token, self.host_address, self.controller_routes['certificates'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a',
                        '--address',
                        help='Address (dev.elasticbox.com by default)',
                        default='https://dev.elasticbox.com')
    parser.add_argument('-e', '--email', help='Your ElasticBox email address')
    parser.add_argument('-p', '--password', help='Your ElasticBox password')

    parser_args = parser.parse_args()

    client = ElasticBoxClient()
    client.log_in(parser_args.address, parser_args.email, parser_args.password)
    client.write_token_to_file()
