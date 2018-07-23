from django.test import TestCase
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from rest_framework_swagger import renderers
from rest_framework_swagger.views import get_swagger_view

from .compat.mock import patch

import requests

local_website = 'localhost'


### Here starts our End-to-end Test for TodoList ##
### -- Start testing the real app ##
class TestKnapAPI(TestCase):

    username = 'amy'

    def setUp(self):
        self.sut = get_swagger_view
        self.factory = APIRequestFactory()
        self.view_class = self.sut().cls

    # Non anonymous CSRF token required by PUT, DELETE, POST (see DRF documentation http://www.django-rest-framework.org/topics/ajax-csrf-cors/)
    @staticmethod
    def add_csrf_header(self):
        # Add todolist
        client = requests.session()
        URL = 'http://' + local_website + '/api-auth/login/'.format(port=80)
        # Retrieve the CSRF token first
        client.get(URL)  # sets cookie
        csrftoken = client.cookies['csrftoken']
        login_data = dict(username=self.username, password=self.username, csrfmiddlewaretoken=csrftoken, next='/')
        response = client.post(URL, data=login_data, headers=dict(Referer=URL))
        self.assertEqual(200, response.status_code)
        return client
    

    def test_request_response(self):
        url = 'http://' + local_website + '/'
        # Send a request to the mock API server and store the response.
        response = requests.get(url)
        # Confirm that the request-response cycle completed successfully.
        self.assertEqual(200, response.status_code)

    def test_users_response(self):
        url = 'http://' + local_website + '/users'
        response = requests.get(url)
        self.assertEqual(200, response.status_code)

    def test_todolist_response(self):
        url = 'http://' + local_website + '/products'
        response = requests.get(url)
        self.assertEqual(200, response.status_code)

## Connection enable, check the todolist CRUD API
    def test_todolist_1_POST_todolist(self):
        client = self.add_csrf_header(self)
        # Add todolist
        URL = 'http://' + local_website + '/products/'
        client.get(URL)
        csrftoken = client.cookies['csrftoken']
        add_todo = dict(title='coca', brand='coca-cola', text='coca', barcode='12346564', language='fr', csrfmiddlewaretoken=csrftoken, next='/')
        response = client.post(URL, data=add_todo, headers=dict(Referer=URL))
        self.assertEqual(201, response.status_code)

    def test_todolist_2_PUT_todolist(self):
        client = self.add_csrf_header(self)
        URL = 'http://' + local_website + '/products/1/'
        client.get(URL)  # sets cookie
        client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
        update_todo = dict(title='coca', brand='coca-cola', text='coca', barcode='12346564', language='fr')
        response = client.put(URL, data=update_todo, headers=dict(Referer=URL))
        self.assertEqual(200, response.status_code)

    def test_todolist_3_DELETE_todolist(self):
        client = self.add_csrf_header(self)
        # Delete an item
        URL = 'http://' + local_website + '/products/1/'
        # Retrieve the CSRF token first
        client.get(URL)  # sets cookie
        client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
        response = client.delete(URL, headers=dict(Referer=URL))
        self.assertEqual(response.content, b'')
        self.assertEqual(204, response.status_code)