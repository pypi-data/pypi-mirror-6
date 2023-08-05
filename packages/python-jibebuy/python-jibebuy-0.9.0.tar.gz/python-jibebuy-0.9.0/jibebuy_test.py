#!/usr/bin/python2.7
# -*- coding: utf-8 -*-#
#
# Copyright 2014 Jibebuy, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import jibebuy


class ApiTest(unittest.TestCase):
    def testApi(self):
        api = jibebuy.Api('http://127.0.0.1:8000/', 'test1@test.com', 'password')
        # Add a new list with post_list
        new_api_list = { 'list_type': 'http://127.0.0.1:8000/api/list-types/1', 'list_type_name': 'Test', 'name': 'Test API List 1', 'description': 'This is a test list'}
        response = api.post_list(new_api_list)
        # New list should be returned as JSON
        list = response.json()
        self.assertEqual(list['name'], 'Test API List 1')

        # Update our new list
        list['description'] = 'This is a test list post'
        response = api.put_list(list)
        list = response.json()
        self.assertEqual(list['description'], 'This is a test list post')

        # Add a choice to our list
        new_api_choice = { 'list': list['url'], 'name': 'Test API Choice 1', 'description': 'This is a test choice'}
        response = api.post_list_choice(new_api_choice)
        choice = response.json()
        self.assertEqual(choice['name'], 'Test API Choice 1')

        api.delete_list(list['id'])


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ApiTest))
    return suite

if __name__ == '__main__':
    unittest.main()
