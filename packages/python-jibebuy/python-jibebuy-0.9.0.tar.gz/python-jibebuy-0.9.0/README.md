# Python Jibebuy

**A Python wrapper for the Jibebuy REST API**

Author: Jibebuy, Inc. <support@jibebuy.com>

## Introduction

[Jibebuy](http://www.jibebuy.com) Jibebuy is a free service to make complex shopping decisions more efficient and
enjoyable. Jibebuy has a [REST web service](http://www.jibebuy.com/api). This library provides a Python friendly
wrapper for the Jibebuy REST API.

## Installing

Install the official release from PyPI:

    $ pip install python-jibebuy

Install the latest from github:

    $ pip install https://github.com/pjtpj/python-jibebuy/zipball/master

## Getting the code

The code is hosted at [Github](https://github.com/pjtpj/python-jibebuy).

Check out the latest development version anonymously with:

```
 $ git clone git://github.com/pjtpj/python-jibebuy.git
 $ cd python-jibebuy
```

## Building

Install the dependencies:

- [requests](https://github.com/kennethreitz/requests)

Download the latest `python-jibebuy` library from: https://github.com/pjtpj/python-jibebuy

Extract the source distribution and run:

```
$ python setup.py build
$ python setup.py install
```

*Testing*

With setuptools installed:

```
$ python setup.py test
```

Without setuptools installed:

```
$ python jibebuy_test.py
```

## Using

The library provides a Python wrapper around the Jibebuy REST API. To use the Jibebuy REST API, you must already have a
Jibebuy account. Create your free Jibebuy account at http://www.jibebuy.com.

The best way to learn how to use the Jibebuy REST API is to login to www.jibebuy.com, then change your URL to
http://www.jibebuy.com/api and explore.

This wrapper relies on the requests library to wrap the Jibebuy REST API. You can read more about requests at
http://docs.python-requests.org/en/latest/.

*API:*

The API is exposed via the `jibebuy.Api` class. Here is an example of its use:

```
>>> import jibebuy
>>> api = jibebuy.Api('http://www.jibebuy.com/', 'username', 'password')
>>> # Add a new list with post_list (list type 1 is "Other")
>>> new_api_list = { 'list_type': 'http://www.jibebuy.com/api/list-types/1', 'list_type_name': 'Test', 'name': 'Test API List 1', 'description': 'This is a test list'}
>>> response = api.post_list(new_api_list)
>>> # New list should be returned as JSON
>>> list = response.json()
>>> # Update our new list
>>> list['description'] = 'This is a test list post'
>>> response = api.put_list(list)
>>> list = response.json()
>>> # Add a choice to our list
>>> new_api_choice = { 'list': list['url'], 'name': 'Test API Choice 1', 'description': 'This is a test choice'}
>>> response = api.post_list_choice(new_api_choice)
>>> choice = response.json()
>>> # Add a photo to the choice
>>> new_api_choice_photo = { 'list_choice': choice['url'] }
>>> response = api.post_list_choice_photo(new_api_choice_photo, open('~/tmp/ebay.png'))
```

## Todo

Patches and bug reports are [welcome](https://github.com/pjtpj/python-jibebuy/issues/new). Please keep the style consistent with the original source.

Add example scripts.

Add more tests.

## Contributors

Initial API wrapper thanks to Ken White

## License

```
Copyright 2014 Jibebuy, Inc.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
