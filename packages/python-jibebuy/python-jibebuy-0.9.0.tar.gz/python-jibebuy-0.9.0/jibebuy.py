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

import json, urllib, pprint, time, re
import requests
import traceback


class Api(object):

    def __init__(self, server_url, username, password):
        # handle possible superfluous trailing "/"
        if str(server_url).endswith("/"):
            self.server_url = server_url[:-1]
        else:
            self.server_url = server_url
        self.username = username
        self.password = password


        url = self.server_url + "/api-token-auth/"
        payload = {'username': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        jsondata =  response.json()
        auth_token = jsondata["token"]
        self.auth_token = auth_token

    def close(self):
        pass
        #self.connection.close()

    @staticmethod
    def _list_url_to_id(urlstr):
        matches = re.search(r"/api/lists/(\d+)$", urlstr)
        return matches.group(1)

    def _url_from_key(self, urlkey, id=None, forlist=None):
        if id:
            requrl = self.server_url + "/api/%s/%d" % (urlkey, id)
        else:
            requrl = self.server_url + "/api/%s" % urlkey   # return all lists

        if forlist:
            # the list can be either an id number or a url
            # (a lot of the objects reference their list by url)
            if isinstance(forlist, (int, long)):
                listval = str(forlist)
            else:
                listval = JibebuyAPI._list_url_to_id(forlist)
            requrl += "?list=" + listval
        return requrl

    # *****************************
    # vvvvvvv GET methods vvvvvvvvv
    # *****************************

    def _get_obj(self, requrl):
        # the authentication token is sent in the headers
        headers = {"Authorization": "Token " + self.auth_token,
                   'Content-Type': 'application/json'}
        response = requests.get(requrl, headers=headers)
        return response

    def get_list(self, id=None, forlist=None):
        requrl = self._url_from_key("lists", id, forlist)
        return self._get_obj(requrl)

    def get_list_photo(self, id=None, forlist=None):
        requrl = self._url_from_key("list-photos", id, forlist)
        return self._get_obj(requrl)

    def get_list_choice(self, id=None, forlist=None):
        requrl = self._url_from_key("list-choices", id, forlist)
        return self._get_obj(requrl)

    def get_list_choice_jibe(self, id=None, forlist=None):
        requrl = self._url_from_key("list-choice-jibes", id, forlist)
        return self._get_obj(requrl)

    def get_list_choice_photo(self, id=None, forlist=None):
        requrl = self._url_from_key("list-choice-photos", id, forlist)
        return self._get_obj(requrl)

    def get_list_share_user(self, id=None, forlist=None):
        requrl = self._url_from_key("list-share-users", id, forlist)
        return self._get_obj(requrl)

    def get_status_message(self, id=None, forlist=None):
        requrl = self._url_from_key("status-messages", id, forlist)
        return self._get_obj(requrl)

    def get_list_share(self, id=None, forlist=None):
        requrl = self._url_from_key("list-shares", id, forlist)
        return self._get_obj(requrl)

    def get_list_choice_comment(self, id=None, forlist=None):
        requrl = self._url_from_key("list-choice-comments", id, forlist)
        return self._get_obj(requrl)

    def get_list_choice_comment_jibe(self, id=None, forlist=None):
        requrl = self._url_from_key("list-choice-comment-jibes", id, forlist)
        return self._get_obj(requrl)

    def get_user(self, id=None, forlist=None):
        requrl = self._url_from_key("display-users", id, forlist)
        return self._get_obj(requrl)

    def get_email(self, id=None, forlist=None):
        requrl = self._url_from_key("emails", id, forlist)
        return self._get_obj(requrl)

    def get_list_type(self, id=None, forlist=None):
        requrl = self._url_from_key("list-types", id, forlist)
        return self._get_obj(requrl)

    def get_list_user(self, id=None, forlist=None):
        requrl = self._url_from_key("list-users", id, forlist)
        return self._get_obj(requrl)

    # *****************************
    # vvvvvvv POST methods vvvvvvvv
    # *****************************

    def _post_obj(self, requrl, obj):
        # the authentication token is sent in the headers
        headers = {"Authorization": "Token " + self.auth_token,
                   "Content-type": "application/json",
                   }
        kwargs = {"data": json.dumps(obj), "headers": headers}
        response = requests.post(requrl, **kwargs)
        return response

    def _post_photo(self, requrl, file_data, obj):
        # the authentication token is sent in the headers
        # Note: photos are sent as part of a multipart POST: do NOT include Content-Type in headers
        headers = {"Authorization": "Token " + self.auth_token}
        
        # the API expects the photo to be named "photo"
        kwargs = {"files": {"photo": file_data},
                  "data": obj,
                  "headers": headers,
                  }
        response = requests.post(requrl, **kwargs)
        return response

    def post_list(self, obj):
        requrl = self._url_from_key("lists")
        return self._post_obj(requrl, obj)

    def post_list_choice(self, obj):
        requrl = self._url_from_key("list-choices")
        return self._post_obj(requrl, obj)

    def post_list_photo(self, obj, file_data):
        requrl = self._url_from_key("list-photos")
        return self._post_photo(requrl, file_data, obj)

    def post_list_choice_photo(self, obj, file_data):
        requrl = self._url_from_key("list-choice-photos")
        return self._post_photo(requrl, file_data, obj)

    def post_list_choice_jibe(self, obj):
        requrl = self._url_from_key("list-choice-jibes")
        return self._post_obj(requrl, obj)
    
    def post_list_share_user(self, obj):
        requrl = self._url_from_key("list-share-users")
        return self._post_obj(requrl, obj)
    
    def post_status_message(self, obj):
        requrl = self._url_from_key("status-messages")
        return self._post_obj(requrl, obj)
    
    def post_list_share(self, obj):
        requrl = self._url_from_key("list-shares")
        return self._post_obj(requrl, obj)
    
    def post_list_choice_comment(self, obj):
        requrl = self._url_from_key("list-choice-comments")
        return self._post_obj(requrl, obj)
    
    def post_list_choice_comment_jibe(self, obj):
        requrl = self._url_from_key("list-choice-comment-jibes")
        return self._post_obj(requrl, obj)
    
    def post_user(self, obj):
        requrl = self._url_from_key("display-users")
        return self._post_obj(requrl, obj)
    
    def post_email(self, obj):
        requrl = self._url_from_key("emails")
        return self._post_obj(requrl, obj)
    
    def post_list_type(self, obj):
        requrl = self._url_from_key("list-types")
        return self._post_obj(requrl, obj)
    
    def post_list_user(self, obj):
        requrl = self._url_from_key("list-users")
        return self._post_obj(requrl, obj)


    # **************************************
    # vvvvvvv PUT (update) methods vvvvvvvv
    # **************************************

    def _put_obj(self, requrl, obj):
        # the authentication token is sent in the headers
        headers = {"Authorization": "Token " + self.auth_token,
                   "Content-type": "application/json",
                   }
        response = requests.put(requrl, data=json.dumps(obj), headers=headers)
        return response


    def put_list(self, obj):
        requrl = self._url_from_key("lists", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_choice(self, obj):
        requrl = self._url_from_key("list-choices", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_photo(self, obj, file_data):
        requrl = self._url_from_key("list-photos", obj["id"])
        return self._put_photo(requrl, file_data, obj)

    def put_list_choice_photo(self, obj, file_data):
        requrl = self._url_from_key("list-choice-photos", obj["id"])
        return self._put_photo(requrl, file_data, obj)

    def put_list_choice_jibe(self, obj):
        requrl = self._url_from_key("list-choice-jibes", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_share_user(self, obj):
        requrl = self._url_from_key("list-share-users", obj["id"])
        return self._put_obj(requrl, obj)

    def put_status_message(self, obj):
        requrl = self._url_from_key("status-messages", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_share(self, obj):
        requrl = self._url_from_key("list-shares", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_choice_comment(self, obj):
        requrl = self._url_from_key("list-choice-comments", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_choice_comment_jibe(self, obj):
        requrl = self._url_from_key("list-choice-comment-jibes", obj["id"])
        return self._put_obj(requrl, obj)

    def put_user(self, obj):
        requrl = self._url_from_key("display-users", obj["id"])
        return self._put_obj(requrl, obj)

    def put_email(self, obj):
        requrl = self._url_from_key("emails", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_type(self, obj):
        requrl = self._url_from_key("list-types", obj["id"])
        return self._put_obj(requrl, obj)

    def put_list_user(self, obj):
        requrl = self._url_from_key("list-users", obj["id"])
        return self._put_obj(requrl, obj)



    # *****************************
    # vvvvvvv DELETE methods vvvvvv
    # *****************************

    def _delete_obj(self, requrl):
        # the authentication token is sent in the headers
        headers = {"Authorization": "Token " + self.auth_token,
                   'Content-Type': 'application/json'}
        response = requests.delete(requrl, headers=headers)
        return response

    def delete_list(self, id):
        requrl = self._url_from_key("lists", id)
        return self._delete_obj(requrl)

    def delete_list_photo(self, id):
        requrl = self._url_from_key("list-photos", id)
        return self._delete_obj(requrl)

    def delete_list_choice(self, id):
        requrl = self._url_from_key("list-choices", id)
        return self._delete_obj(requrl)

    def delete_list_choice_jibe(self, id):
        requrl = self._url_from_key("list-choice-jibes", id)
        return self._delete_obj(requrl)

    def delete_list_choice_photo(self, id):
        requrl = self._url_from_key("list-choice-photos", id)
        return self._delete_obj(requrl)

    def delete_list_share_user(self, id):
        requrl = self._url_from_key("list-share-users", id)
        return self._delete_obj(requrl)

    def delete_status_message(self, id):
        requrl = self._url_from_key("status-messages", id)
        return self._delete_obj(requrl)

    def delete_list_share(self, id):
        requrl = self._url_from_key("list-shares", id)
        return self._delete_obj(requrl)

    def delete_list_choice_comment(self, id):
        requrl = self._url_from_key("list-choice-comments", id)
        return self._delete_obj(requrl)

    def delete_list_choice_comment_jibe(self, id):
        requrl = self._url_from_key("list-choice-comment-jibes", id)
        return self._delete_obj(requrl)

    def delete_user(self, id):
        requrl = self._url_from_key("display-users", id)
        return self._delete_obj(requrl)

    def delete_email(self, id):
        requrl = self._url_from_key("emails", id)
        return self._delete_obj(requrl)

    def delete_list_type(self, id):
        requrl = self._url_from_key("list-types", id)
        return self._delete_obj(requrl)

    def delete_list_user(self, id):
        requrl = self._url_from_key("list-users", id)
        return self._delete_obj(requrl)
