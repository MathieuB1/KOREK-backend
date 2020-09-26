from django.test import TestCase
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from .compat.mock import patch

import requests


from os import urandom
import json

from django.conf import settings

local_website = 'localhost:8000'

import psycopg2

### Here starts our End-to-end Test for TodoList ##
### -- Start testing the real app ##
class TestKnapAPI(TestCase):

    username1 = ['toto1','toto2','toto3','toto4']
    user_group = {}

    def setUp(self):
        self.factory = APIRequestFactory()
        #self.maxDiff = None

    # Create Users
    def test_1_create_user1_POST(self):
        result = []
        for user in self.username1:
            client = requests.session()
            url = 'http://' + local_website + '/register/'
            create_user = dict(username=user, password=user, email=user + '@fr.fr', first_name=user, last_name=user)
            client.get(url)
            response = client.post(url, data=create_user, headers=dict(Referer=url))

            if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
                self.user_group[user] = {'group_name' : json.loads(response.content.decode('utf-8'))['groups'][0]['name'], 'group_id' : '', 'user_id': json.loads(response.content.decode('utf-8'))['id']}
            else:
                self.user_group[user] = {'user_id': json.loads(response.content.decode('utf-8'))['id']}

            result.append(response.status_code)

        # Confirm that the request-response cycle completed successfully.
        self.assertEqual([201,201,201,201], result)


    # Non anonymous CSRF token required by PUT, DELETE, POST (see DRF documentation http://www.django-rest-framework.org/topics/ajax-csrf-cors/)
    @staticmethod
    def add_csrf_header(self, user):
        # Add todolist
        client = requests.session()
        URL = 'http://' + local_website + '/api-auth/login/'.format(port=8000)
        # Retrieve the CSRF token first
        client.get(URL)  # sets cookie
        csrftoken = client.cookies['csrftoken']
        login_data = dict(username=user, password=user, csrfmiddlewaretoken=csrftoken, next='/')
        response = client.post(URL, data=login_data, headers=dict(Referer=URL))
        #self.assertEqual(200, response.status_code)
        return client

    def test_1_reset_password(self):

        # Anonymous User
        client = requests.session()
        URL = 'http://' + local_website + '/api-auth/login/'
        client.get(URL)
        csrftoken = client.cookies['csrftoken']
        client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})

        # Change toto1 password
        mail = 'toto1@fr.fr'
        URL = 'http://' + local_website + '/password_reset/'
        add_userpass = dict(user_email=mail, password='toto1', csrfmiddlewaretoken=csrftoken)
        response = client.post(URL, data=add_userpass, headers=dict(Referer=URL))

        if settings.EMAIL_HOST_USER[0] != 'xxxx.yyy@gmail.com':
            self.assertEqual('{"user_email":"' + mail + '"}', response.text)

        # Read the link
        conn = psycopg2.connect(database="korek_db", user = "postgres", password = "postgres", host = "postgres_korek", port = "5432")
        cur = conn.cursor()
        cur.execute("SELECT tmp_url FROM public.korek_passwordreset WHERE user_email='" + str(mail) + "';")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Go to link & validate password change
        URL = 'http://' + str(rows[0][0])
        response = client.get(URL)
        self.assertEqual(200, response.status_code)




    def test_2_addproduct_to_users_POST(self):
        result = []
        for user in self.username1:
            for i in range(2):
                client = self.add_csrf_header(self,user)
                # Add todolist
                URL = 'http://' + local_website + '/products/'
                client.get(URL)
                csrftoken = client.cookies['csrftoken']
                add_product = dict(title='coca', brand='coca-cool', text='coca', barcode='12346564', language='fr', locations='[{"coords": [57.434996, -20.299393]}]', csrfmiddlewaretoken=csrftoken, next='/')
                response = client.post(URL, data=add_product, headers=dict(Referer=URL))
                result.append(response.status_code)

        # Confirm that the request-response cycle completed successfully.
        self.assertEqual([201,201,201,201,201,201,201,201], result)


    def test_3_request_token_POST(self):
        result = []
        for user in self.username1:
            for i in range(1):
                client = requests.session()

                URL = 'http://' + local_website + '/api-auth/login/'
                # Retrieve the CSRF token first
                client.get(URL)  # sets cookie
                csrftoken = client.cookies['csrftoken']
                
                # Add todolist
                URL = 'http://' + local_website + '/api-token-auth/'
                user_post = dict(username=user, password=user, next='/')
                response = client.post(URL, data=user_post, headers=dict(Referer=URL))
                my_token = json.loads(response.content.decode('utf-8'))['token']

                client.headers.update({'Accept': 'application/json'})
                client.headers.update({'Authorization': 'Bearer ' + str(my_token)})

                URL = 'http://' + local_website + '/products/'
                add_product = dict(title='coca', brand='coca-cool', text='coca', barcode='12346564', language='fr', csrfmiddlewaretoken=csrftoken, next='/')
                response = client.post(URL, data=add_product, headers=dict(Referer=URL))
                result.append(response.status_code)

            break

        self.assertEqual([201], result)


    def test_4_add_totoX_to_totoX_PUT(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):

            result = []
            for user in self.username1:
                client = self.add_csrf_header(self,user)
                url = 'http://' + local_website + '/groups/'
                response = client.get(url)
                self.user_group[user]['group_id'] = json.loads(response.content.decode('utf-8'))['results'][0]['id']
                result.append(response.status_code)

            # Confirm that the request-response cycle completed successfully.
            self.assertEqual([200,200,200,200], result)


            # Add toto1 to toto2
            client = self.add_csrf_header(self,'toto1')
            url = 'http://' + local_website + '/groups/' + str(self.user_group['toto1']['group_id']) + '/'
            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            client.headers.update({'Content-Type': 'application/json'})

            add_group = dict(groups=[{'name': 'toto2'}], next='/')
            response = self.factory.put(url, add_group)

            response = client.put(url, data=json.dumps(add_group), headers=client.headers)

            count = 0
            for el in json.loads(response.content.decode('utf-8'))['groups']:
                count += 1
            
            if settings.PRIVACY_MODE[0] == ('PRIVATE-VALIDATION'):
                self.assertEqual(1, count)
            else:
                self.assertEqual(2, count)
                
            self.assertEqual(200, response.status_code)

            # Add toto3 to toto2
            client = self.add_csrf_header(self,'toto3')
            url = 'http://' + local_website + '/groups/' + str(self.user_group['toto3']['group_id']) + '/'

            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            client.headers.update({'Content-Type': 'application/json'})

            add_group = dict(groups=[{'name': 'toto2'}], next='/')
            response = client.put(url, data=json.dumps(add_group), headers=client.headers)

            count = 0
            for el in json.loads(response.content.decode('utf-8'))['groups']:
                count += 1

            if settings.PRIVACY_MODE[0] == ('PRIVATE-VALIDATION'):
                self.assertEqual(1, count)
            else:
                self.assertEqual(2, count)

            self.assertEqual(200, response.status_code)


            # Add toto3 to toto4 & toto1
            client = self.add_csrf_header(self,'toto3')
            url = 'http://' + local_website + '/groups/' + str(self.user_group['toto3']['group_id']) + '/'

            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            client.headers.update({'Content-Type': 'application/json'})

            add_group = dict(groups=[{'name':'toto4'}], next='/')
            response = client.put(url, data=json.dumps(add_group), headers=client.headers)

            add_group = dict(groups=[{'name': 'toto1'}], next='/')
            response = client.put(url, data=json.dumps(add_group), headers=client.headers)

            count = 0
            for el in json.loads(response.content.decode('utf-8'))['groups']:
                count += 1

            if settings.PRIVACY_MODE[0] == ('PRIVATE-VALIDATION'):
                self.assertEqual(1, count)
            else:
                self.assertEqual(4, count)

            self.assertEqual(200, response.status_code)

        # Validates Users
        if settings.PRIVACY_MODE[0] == 'PRIVATE-VALIDATION':

            for user in self.username1:
                client = self.add_csrf_header(self,user)
                url = 'http://' + local_website + '/acknowlegment/'
                response = client.get(url)

                ids = []
                for x in json.loads(response.content.decode('utf-8'))['results']:
                    ids.append(x['id'])

                client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
                client.headers.update({'Content-Type': 'application/json'})

                for id in ids:
                    url = 'http://' + local_website + '/acknowlegment/' + str(id) + '/'
                    add_group = dict(activate="true", next='/')
                    response = client.put(url, data=json.dumps(add_group), headers=client.headers)
                    
                    self.assertEqual(True, json.loads(response.content.decode('utf-8'))['activate'])
                    self.assertEqual(200, response.status_code)


    def test_5_access_media_POST(self):
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            client = self.add_csrf_header(self,'toto1')
            URL = 'http://' + local_website + '/products/'
            client.get(URL)
            csrftoken = client.cookies['csrftoken']
            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            # test permission
            result = []
            with open('/code/tests/plan_fr.jpg', 'rb') as f:
                URL = 'http://' + local_website + '/products/'
                client.headers.update({'Accept': 'application/json'})
                add_product = dict(title='coca', brand='coca-cool', text='coca', barcode='12346564', language='fr', format='multipart', next='/')
                response = client.post(URL, data=add_product, files={'upload_file': f}, headers=dict(Referer=URL))
                result.append(response.status_code)
                res = json.loads(response.text)['images'][0]['image']

                response = client.get(res)
                result.append(response.status_code)
            
            # another user access
            client = self.add_csrf_header(self,'toto2')
            URL = 'http://' + local_website + '/products/'
            client.get(URL)
            csrftoken = client.cookies['csrftoken']
            response = client.get(res)
            result.append(response.status_code)

            # forbidden user access
            client = self.add_csrf_header(self,'toto4')
            URL = 'http://' + local_website + '/products/'
            client.get(URL)
            csrftoken = client.cookies['csrftoken']
            response = client.get(res)
            result.append(response.status_code)

            self.assertEqual([201, 200, 200, 403], result)


    def test_6_validate_access_to_users_POST(self):
        result = []
        list_friends = []
        for user in self.username1:
            client = self.add_csrf_header(self,user)
            url = 'http://' + local_website + '/products/'
            response = client.get(url)

            friends = set()
            for x in json.loads(response.content.decode('utf-8'))['results']:
                friends.add(x['owner'])

            result.append(response.status_code)
            list_friends.append(friends)

        # toto1, toto2, toto3, toto4 friends
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            self.assertEqual(list_friends.sort(), [{'toto2', 'toto3', 'toto1'}, {'toto3', 'toto1', 'toto2'}, {'toto3', 'toto4', 'toto1', 'toto2'}, {'toto4', 'toto3'}].sort())
        else:
            self.assertEqual(list_friends.sort(), [{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'}].sort())
        # Confirm that the request-response cycle completed successfully.
        self.assertEqual([200,200,200,200], result)


    def test_6_validate_access_to_users_POST(self):
        result = []
        list_friends = []
        for user in self.username1:
            client = self.add_csrf_header(self,user)
            url = 'http://' + local_website + '/products/'
            response = client.get(url)

            friends = set()
            for x in json.loads(response.content.decode('utf-8'))['results']:
                friends.add(x['owner'])

            result.append(response.status_code)
            list_friends.append(friends)

        # toto1, toto2, toto3, toto4 friends
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            self.assertEqual(list_friends.sort(), [{'toto2', 'toto3', 'toto1'}, {'toto3', 'toto1', 'toto2'}, {'toto3', 'toto4', 'toto1', 'toto2'}, {'toto4', 'toto3'}].sort())
        else:
            self.assertEqual(list_friends.sort(), [{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'},{'toto2', 'toto1', 'toto3', 'toto4'}].sort())
        # Confirm that the request-response cycle completed successfully.
        self.assertEqual([200,200,200,200], result)


    def test_7_test_intersect_GET(self):
        user = 'toto1'
        client = self.add_csrf_header(self,user)
        url = 'http://' + local_website + '/intersect/?bbox=-180.00 90.00,180.00 90.00,180.00 -90.00,-180.00 -90.00'
        response = client.get(url)

        self.assertEqual(6, response.json()['count'])
        
        for el in response.json()['results']:
            self.assertEqual(True, isinstance(el['product'], int))
            self.assertEqual('SRID=4326;POINT (57.434996 -20.299393)', el['coords'])

                
        csrftoken = client.cookies['csrftoken']
        
        # Add todolist
        URL = 'http://' + local_website + '/api-token-auth/'
        user_post = dict(username=user, password=user, next='/')
        response = client.post(URL, data=user_post, headers=dict(Referer=URL))
        my_token = json.loads(response.content.decode('utf-8'))['token']

        client.headers.update({'Accept': 'application/json'})
        client.headers.update({'Authorization': 'Bearer ' + str(my_token)})

        # Create Antibes point location
        URL = 'http://' + local_website + '/products/'
        add_product = dict(title='antibes', text='antibes location point', language='fr', locations='[{"coords": [7.111101, 43.580315]}]', csrfmiddlewaretoken=csrftoken, next='/')
        response = client.post(URL, data=add_product, headers=dict(Referer=URL))
        self.assertEqual(201, response.status_code)

        URL = 'http://' + local_website + '/products/'
        add_product = dict(title='mauritius', text='mauritius location point', language='fr', locations='[{"coords": [57.434996, -20.299393]}]', csrfmiddlewaretoken=csrftoken, next='/')
        response = client.post(URL, data=add_product, headers=dict(Referer=URL))
        self.assertEqual(201, response.status_code)

        # Antibes is within this intersection
        url = 'http://' + local_website + '/intersect/?bbox=2.412835 46.358776,8.342991 45.779496,8.518699 41.026017,3.291377 41.389688'
        response = client.get(url)
        self.assertEqual(1, response.json()['count'])
        self.assertEqual('SRID=4326;POINT (7.111101 43.580315)', response.json()['results'][0]['coords'])

        # Mauritius is within this intersection
        url = 'http://' + local_website + '/intersect/?bbox=56.402710 -19.638546,58.785754 -19.617850,58.774854 -21.121494,56.490646 -21.131742'
        response = client.get(url)
        self.assertEqual(7, response.json()['count'])
        self.assertEqual('SRID=4326;POINT (57.434996 -20.299393)', response.json()['results'][0]['coords'])


    def test_8_test_search_GET(self):
        user = 'toto1'
        client = self.add_csrf_header(self,user)
        url = 'http://' + local_website + '/products/?search=mauritius location point'
        response = client.get(url)
        self.assertEqual(1, response.json()['count'])
    
        url = 'http://' + local_website + '/products/?search=mauritius point'
        response = client.get(url)
        self.assertEqual(1, response.json()['count'])


    def test_8_test_search_GET_zipped(self):
        user = 'toto1'
        client = self.add_csrf_header(self,user)
        url = 'http://' + local_website + '/products/?search=mauritius&zip=true'
        response = client.get(url)
        self.assertEqual(True, isinstance(response.json()['count'], int))


    def test_9_delete_product_POST(self):
        result = []
        client = self.add_csrf_header(self,'toto2')
        url = 'http://' + local_website + '/products/'
        response = client.get(url)

        # Delete toto2 products
        for x in json.loads(response.content.decode('utf-8'))['results']:
            url = 'http://' + local_website + '/products/' + str(x['id']) + '/'

            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            response = client.delete(url, headers=dict(Referer=url))
            result.append(response.status_code)

        url = 'http://' + local_website + '/products/'
        response = client.get(url)

        # toto2 has toto1 and toto 3 products
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            self.assertEqual(8,json.loads(response.content.decode('utf-8'))['count'])
        else:
            self.assertEqual(9,json.loads(response.content.decode('utf-8'))['count'])

        res = []
        for x in json.loads(response.content.decode('utf-8'))['results']:
            res.append(str(x['owner']))
   
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            self.assertEqual(['toto1','toto1','toto1','toto1','toto3','toto3','toto1','toto1'], res)
        else:
            self.assertEqual(['toto1','toto1','toto1', 'toto4', 'toto4', 'toto3', 'toto3', 'toto1', 'toto1'], res)

        # Confirm that the request-response cycle completed successfully.
        if settings.PRIVACY_MODE[0].startswith('PRIVATE'):
            self.assertEqual([403, 403, 403, 403, 403, 403, 204, 204, 403, 403], result)
        else:
            self.assertEqual([403, 403, 403, 403, 403, 403, 204, 204, 403, 403, 403], result)


    def test_9_users_DELETE(self):

        result = []
        for user in self.username1:
            client = self.add_csrf_header(self,user)
            url = 'http://' + local_website + '/register/' + str(self.user_group[user]['user_id']) + '/'
            client.get(url)
            client.headers.update({"X-CSRFTOKEN": client.cookies['csrftoken']})
            response = client.delete(url, headers=dict(Referer=url))
            result.append(response.status_code)

        # Confirm that the request-response cycle completed successfully.
        self.assertEqual([204,204,204,204], result)