import argparse
import json
import sys
import time

import cloud_elements


__author__ = 'jjwyse'


class ElementsTester():
    def __init__(self, hub_name):

        self.api_endpoints = {
            'snapshot': 'https://snapshot.cloud-elements.com/elements/api-v1',
            'qa': 'https://qa.cloud-elements.com/elements/api-v1',
            'production': 'https://console.cloud-elements.com/elements/api-v1'
        }
        command_line_args = self.__load_command_line_args()

        endpoint = self.api_endpoints[command_line_args.environment]
        element_token = command_line_args.element_token
        self.is_verbose = command_line_args.verbose
        self.failed_apis = {}

        # create our elements connector
        self.elements_connector = ElementsConnectorTest(provider_name=hub_name, element_token=element_token,
                                                        api_endpoint=endpoint)

    def ping(self):
        response = self.elements_connector.make_get_request(api='ping', params=None)
        if self.is_failed(response):
            print 'FAIL: ping failed, exiting'
            sys.exit(1)

    def get(self, api, params=None):
        response = self.elements_connector.make_get_request(api=api, params=params)
        self.handle_response(api, response)

    def post(self, api, root_json_name=None, params=None, payload=None, files=None):
        response = self.elements_connector.make_post_request(api=api, params=params, payload=payload, files=files)
        self.handle_response(api, response)
        return ElementsTester.find_id(response, root_json_name)

    def put(self, api, params=None, payload=None, files=None):
        response = self.elements_connector.make_put_request(api=api, params=params, payload=payload, files=files)
        self.handle_response(api, response)

    def delete(self, api, params=None):
        response = self.elements_connector.make_delete_request(api=api, params=params)
        self.handle_response(api, response)

    def finished(self):
        self.print_failed_apis()

    def __load_command_line_args(self):
        parser = argparse.ArgumentParser(description='Script to test the Cloud Elements APIs')
        parser.add_argument('-e', '--environment', help='localhost or snapshot or qa or production', required=True)
        parser.add_argument('-t', '--element_token', help='Element token', required=True)
        parser.add_argument('-p', '--port', help='If --environment=localhost, this is required', required=False)
        parser.add_argument('-v', '--verbose', help='Turn on verbose output.', action='store_true')
        loaded_args = parser.parse_args()

        environment = loaded_args.environment
        if environment == 'localhost' and not loaded_args.port:
            print 'Must specify --port if running against localhost'
            sys.exit(1)

        if loaded_args.port and environment == 'localhost':
            environment = 'localhost:' + loaded_args.port
            self.api_endpoints['localhost'] = 'http://localhost:' + loaded_args.port + '/elements/api-v1'
        print ""
        print "command line args:"
        print "=================="
        print "environment:\t" + environment
        print "element_token:\t" + loaded_args.element_token
        print "verbose:\t" + str(loaded_args.verbose)
        print ""

        return loaded_args

    def print_failed_apis(self):
        if len(self.failed_apis) is 0:
            print "\nsuccess\n"
            sys.exit(0)
        print "\nfailed apis:\n============\n"
        for api_method_name, json_response in self.failed_apis.items():
            print "\n" + api_method_name
            print ElementsTester.print_json(json_response)
        print ""
        sys.exit(1)

    def handle_response(self, api_method_name, response):
        if self.is_failed(response):
            self.failed_apis[api_method_name] = response

        if self.is_verbose:
            self.print_json(response)


    @staticmethod
    def find_id(response, root_json_name):
        if response.get('id'):
            return response['id']
        if root_json_name is not None and response.get(root_json_name):
            return response[root_json_name]['id']
        return None

    @staticmethod
    def print_json(data):
        print json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '))

    @staticmethod
    def is_failed(response):
        if response.get('success') is None or response.get('success') is False:
            return True
        else:
            return False


class ElementsTimer():
    def __init__(self):
        pass

    @staticmethod
    def time_me(method):
        def wrapper(*method_args, **kw):
            start_time = int(round(time.time() * 1000))
            result = method(*method_args, **kw)
            end_time = int(round(time.time() * 1000))

            length = end_time - start_time
            print '%s - %s ms' % (kw['api'], length)
            return result

        return wrapper


class ElementsConnectorTest(cloud_elements.ElementsConnector):
    def __init__(self, provider_name, element_token, api_endpoint='https://console.cloud-elements.com/elements/api-v1'):
        cloud_elements.ElementsConnector.__init__(self, API_ENDPOINT=api_endpoint)
        self.provider_name = provider_name
        self.element_token = element_token

    @ElementsTimer.time_me
    def invoke(self, http_method, hub_name, element_token, api, version='1', params=None, payload=None, files=None):
        return cloud_elements.ElementsConnector.invoke(self, httpMethod=http_method, providerName=hub_name,
                                                       elementToken=element_token, apiMethodName=api,
                                                       providerVersion=version, params=params,
                                                       payload=payload,
                                                       files=files)

    def make_post_request(self, api, params, payload, files):
        return self.invoke(http_method='post', hub_name=self.provider_name,
                           element_token=self.element_token,
                           api=api, params=params, payload=payload, files=files)


    def make_get_request(self, api, params):
        return self.invoke(http_method='get', hub_name=self.provider_name,
                           element_token=self.element_token, api=api, params=params)


    def make_put_request(self, api, params, payload, files):
        return self.invoke(http_method='put', hub_name=self.provider_name,
                           element_token=self.element_token,
                           api=api, params=params, payload=payload, files=files)


    def make_delete_request(self, api, params):
        return self.invoke(http_method='delete', hub_name=self.provider_name,
                           element_token=self.element_token, api=api, params=params)
