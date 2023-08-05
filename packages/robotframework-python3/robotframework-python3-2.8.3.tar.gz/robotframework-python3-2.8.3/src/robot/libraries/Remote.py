#  Copyright 2008-2013 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import xmlrpclib
import socket
import time
import sys
try:
    from xml.parsers.expat import ExpatError
except ImportError:   # No expat in IronPython 2.7
    class ExpatError(Exception):
        pass

from robot.errors import RemoteError
from robot.utils import is_list_like, is_dict_like, unic


class Remote(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, uri='http://localhost:8270'):
        if '://' not in uri:
            uri = 'http://' + uri
        self._uri = uri
        self._client = XmlRpcRemoteClient(uri)

    def get_keyword_names(self, attempts=5):
        for i in range(attempts):
            try:
                return self._client.get_keyword_names()
            except TypeError, err:
                time.sleep(1)
        raise RuntimeError('Connecting remote server at %s failed: %s'
                           % (self._uri, err))

    def get_keyword_arguments(self, name):
        try:
            return self._client.get_keyword_arguments(name)
        except TypeError:
            return ['*args']

    def get_keyword_documentation(self, name):
        try:
            return self._client.get_keyword_documentation(name)
        except TypeError:
            return ''

    def run_keyword(self, name, args, kwargs):
        args = self._handle_argument(args)
        kwargs = self._handle_argument(kwargs)
        result = RemoteResult(self._client.run_keyword(name, args, kwargs))
        sys.stdout.write(result.output)
        if result.status != 'PASS':
            raise RemoteError(result.error, result.traceback)
        return result.return_

    def _handle_argument(self, arg):
        if isinstance(arg, (basestring, int, long, float)):
            return arg
        if is_list_like(arg):
            return [self._handle_argument(item) for item in arg]
        if is_dict_like(arg):
            return dict((self._str(key), self._handle_argument(value))
                        for key, value in arg.items())
        return self._str(arg)

    def _str(self, item):
        if item is None:
            return ''
        return unic(item)


class RemoteResult(object):

    def __init__(self, result):
        try:
            self.status = result['status']
            self.output = result.get('output', '')
            self.return_ = result.get('return', '')
            self.error = result.get('error', '')
            self.traceback = result.get('traceback', '')
        except (KeyError, AttributeError):
            raise RuntimeError('Invalid remote result dictionary: %s' % result)


class XmlRpcRemoteClient(object):

    def __init__(self, uri):
        self._server = xmlrpclib.ServerProxy(uri, encoding='UTF-8')

    def get_keyword_names(self):
        try:
            return self._server.get_keyword_names()
        except socket.error, (errno, err):
            raise TypeError(err)
        except xmlrpclib.Error, err:
            raise TypeError(err)

    def get_keyword_arguments(self, name):
        try:
            return self._server.get_keyword_arguments(name)
        except xmlrpclib.Error:
            raise TypeError

    def get_keyword_documentation(self, name):
        try:
            return self._server.get_keyword_documentation(name)
        except xmlrpclib.Error:
            raise TypeError

    def run_keyword(self, name, args, kwargs):
        run_keyword_args = [name, args, kwargs] if kwargs else [name, args]
        try:
            return self._server.run_keyword(*run_keyword_args)
        except xmlrpclib.Error, err:
            raise RuntimeError(err.faultString)
        except socket.error, (errno, err):
            raise RuntimeError('Connection to remote server broken: %s' % err)
        except ExpatError, err:
            raise RuntimeError('Processing XML-RPC return value failed. '
                               'Most often this happens when the return value '
                               'contains characters that are not valid in XML. '
                               'Original error was: ExpatError: %s' % err)
