import json
import os
import pymongo
import urllib
from django.test import TestCase
from cloudengine.testclient import MyTestClient


class ClassViewTest(TestCase):
    # testData.json creates testclient user for running tests
    fixtures = ['testClient.json']
    # store user data fixtures in classes/fixtures directory only
    myfixtures = ['classes.json']
    client_class = MyTestClient
    maxDiff = None

    def setUp(self):
        # cannot use django TestCase fixtures to load mongo data
        # hence load it here
        self.client
        dbclient = pymongo.MongoClient()
        self.dbclient = dbclient
        cur_filepath = os.path.abspath(__file__)
        cur_dir = os.path.dirname(cur_filepath)
        db = dbclient.testapp
        for fixture in self.myfixtures:
            new_fixture = os.path.join(cur_dir, "fixtures", fixture)
            f = open(new_fixture)
            collections = json.loads(f.read())
            self.loaded_data = collections
            for collection in collections:
                collection = db[collection]
                objs = collections[collection]
                collection.insert(objs)

    def tearDown(self):
        self.dbclient.drop_database("testapp")

    def test_get_all_classes(self):
        response = self.client.get('/api/v1/classes/')
        # get on classes is root is not currently supported
        # add support for this??
        self.assertEqual(response.status_code, 404)

    def test_create_class(self):
        # create body yourself. django test client bungles
        # encoding if given raw dict
        body = '{"name": "player1", "score": 1234}'
        response = self.client.post('/api/v1/classes/players/',
                                    body,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        res = json.loads(response.content)
        objid = res["_id"]
        # get the created class
        response = self.client.get('/api/v1/classes/players/%s/' % objid)
        body_json = json.loads(body)
        body_json["_id"] = objid
        expected = {"result": body_json}
        # assert json instead of raw string since the
        # order of keys could be different
        self.assertJSONEqual(response.content, expected)

    def test_get_class(self):
        response = self.client.get('/api/v1/classes/persons/')
        self.assertEqual(response.status_code, 200)
        persons = list(self.loaded_data['persons'])
        for person in persons:
            person.pop('app_id')
        expected_data = {"result": persons}
        self.assertJSONEqual(response.content, expected_data)

    def test_empty_query(self):
        query = {"query": '{}'}
        qstr = urllib.urlencode(query)
        response = self.client.get('/api/v1/classes/persons/?%s' % qstr)
        self.assertEqual(response.status_code, 200)
        persons = list(self.loaded_data['persons'])
        for person in persons:
            person.pop('app_id')
        expected_data = {"result": persons}
        self.assertJSONEqual(response.content, expected_data)

    def test_query_gt(self):
        query = {"query": '{"age" : {"$gt" : 50}}'}
        qstr = urllib.urlencode(query)
        response = self.client.get('/api/v1/classes/persons/?%s' % qstr)
        self.assertEqual(response.status_code, 200)
        persons = list(self.loaded_data['persons'])
        gt_list = [person for person in persons if person['age'] > 50]
        for person in gt_list:
            person.pop('app_id')
        expected_data = {"result": gt_list}
        self.assertJSONEqual(response.content, expected_data)

    def test_query_lt(self):
        query = {"query": '{"age" : {"$lt" : 50}}'}
        qstr = urllib.urlencode(query)
        response = self.client.get('/api/v1/classes/persons/?%s' % qstr)
        self.assertEqual(response.status_code, 200)
        persons = list(self.loaded_data['persons'])
        lt_list = [person for person in persons if person['age'] < 50]
        for person in lt_list:
            person.pop('app_id')
        expected_data = {"result": lt_list}
        self.assertJSONEqual(response.content, expected_data)

    def test_query_gt_lt(self):
        query = {"query": '{"age" : {"$gt" : 50, "$lt" : 70}}'}
        qstr = urllib.urlencode(query)
        response = self.client.get('/api/v1/classes/persons/?%s' % qstr)
        self.assertEqual(response.status_code, 200)
        persons = list(self.loaded_data['persons'])
        gt_lt_list = [person for person in persons if 50 < person['age'] < 70]
        for person in gt_lt_list:
            person.pop('app_id')
        expected_data = {"result": gt_lt_list}
        self.assertJSONEqual(response.content, expected_data)
