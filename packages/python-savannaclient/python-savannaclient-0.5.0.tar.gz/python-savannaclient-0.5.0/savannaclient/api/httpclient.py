# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests


class HTTPClient(object):
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def get(self, url):
        return requests.get(self.base_url + url,
                            headers={'x-auth-token': self.token})

    def post(self, url, body):
        return requests.post(self.base_url + url, body,
                             headers={'x-auth-token': self.token,
                                      'content-type': 'application/json'})

    def put(self, url, body):
        return requests.put(self.base_url + url, body,
                            headers={'x-auth-token': self.token,
                                     'content-type': 'application/json'})

    def delete(self, url):
        return requests.delete(self.base_url + url,
                               headers={'x-auth-token': self.token})
