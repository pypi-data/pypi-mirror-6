#-*- coding: utf-8 -*-

# messy functional tests. Refactor needed.
# functional tests for the auto api feature.
# here some models are created, an auto restful api is
# configured an then we run tests on it

import sys
import os
import copy
import requests
from mongoengine import Document
from mongoengine.fields import StringField, ReferenceField, IntField
from tornado.web import Application
from pyrocumulus.tornadoweb import RestHandler
from pyrocumulus.conf import get_settings_module
from pyrocumulus.db import MongoConnection
from pyrocumulus.testing import TornadoApplicationTestCase


settings = get_settings_module('settings_test')
db_settings = settings.DATABASE['default']

connection = MongoConnection(db_settings['db'],
                             host=db_settings['host'],
                             port=db_settings['port'])
connection.connect()


class MyFirstDocument(Document):
    name = StringField(required=True, unique=True)
    nice_attribute = StringField()
    other_attribute = IntField()


class OtherDocument(Document):
    attribute = StringField()
    ref = ReferenceField(MyFirstDocument)


urls = [(r'/api/myfirstdocument/(.*)', RestHandler,
         dict(model=MyFirstDocument)),
        (r'/api/otherdocument/(.*)', RestHandler,
         dict(model=OtherDocument))]

application = Application(urls, debug=True)



class MyFirstDocumentAPITestCase(TornadoApplicationTestCase):

    # exclude it from examples
    @classmethod
    def setUpClass(cls):
        cls.python_exec = cls._get_python_exec()
        cls.application = 'functional_tests.test_autoapi.application'
        super(MyFirstDocumentAPITestCase, cls).setUpClass()

    @classmethod
    def _get_python_exec(cls):
        # hack to call the correct intepreter on
        # buildbot.

        env = [p for p in sys.argv if '--tornadoenv=' in p]
        if env:
            env = env[0].split('=')[1]
        else:
            return 'python'
        return os.path.join(env, os.path.join('bin', 'python'))
    
    # end exclude it

    def setUp(self):
        self.base_url = 'http://localhost:8888/api/myfirstdocument/'
        self.params = {'nice_attribute': "I'm nice",
                       'other_attribute': 0}

        self.populate_db()
        
    def populate_db(self):
        """
        create some objects before the test start so we can
        perform our functional tests with some data
        """
        self.objects_list = []
        for i in range(10):
            obj = MyFirstDocument(self.params)
            obj.name = 'name %s' % i
            obj.save()
            self.objects_list.append(obj)

    def tearDown(self):
        MyFirstDocument.drop_collection()

    def test_create(self):
        params = copy.copy(self.params)
        params.update({'name': 'my unique name'})
        response = requests.put(self.base_url, params)
        response.connection.close()
        self.assertTrue(response.json()['id'])

    def test_create_without_required_field(self):
        response = requests.put(self.base_url, self.params)
        response.connection.close()
        self.assertEqual(response.status_code, 500)

    def test_get(self):
        doc_id = self.objects_list[0].id
        response = requests.get(self.base_url, params={'id': doc_id})
        response.connection.close()

        self.assertEqual(response.json()['name'], self.objects_list[0].name)

    def test_list(self):
        response = requests.get(self.base_url + 'list')
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 10)

    def test_list_with_filter(self):
        response = requests.get(self.base_url + 'list',
                                params={'name': 'name 2'})
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 1)

    def test_delete(self):
        response = requests.delete(self.base_url,
                                   params={'id': self.objects_list[0].id})
        response.connection.close()
        response = requests.get(self.base_url + 'list')
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 9)


class OtherDocumentAPITestCase(TornadoApplicationTestCase):

    # exclude it from examples
    @classmethod
    def setUpClass(cls):
        cls.python_exec = cls._get_python_exec()
        cls.application = 'functional_tests.test_autoapi.application'
        super(OtherDocumentAPITestCase, cls).setUpClass()

    @classmethod
    def _get_python_exec(cls):
        # hack to call the correct intepreter on
        # buildbot.

        env = [p for p in sys.argv if '--tornadoenv=' in p]
        if env:
            env = env[0].split('=')[1]
        else:
            return 'python'
        return os.path.join(env, os.path.join('bin', 'python'))
    
    # end exclude it

    def setUp(self):
        self.base_url = 'http://localhost:8888/api/otherdocument/'
        self.params = {'attribute': 'Wow!'}
        self.populate_db()

    def populate_db(self):
        self.relateds = [MyFirstDocument(name='name 1',
                                         nice_attribute='nice!',
                                         other_attribute=1).save(),
                         MyFirstDocument(name='name 2',
                                         nice_attribute='yeah yeah!',
                                         other_attribute=2).save()]
                                        
        for i in range(10):
            self.documents = []
            doc = OtherDocument(attribute='ueba! %s' % i)
            if i < 6:
                doc.ref = self.relateds[0]
            else:
                doc.ref = self.relateds[1]
            doc.save()
            self.documents.append(doc)

    def tearDown(self):
        MyFirstDocument.drop_collection()
        OtherDocument.drop_collection()

    def test_create(self):
        response = requests.put(self.base_url, self.params)
        response.connection.close()
        self.assertTrue(response.json()['id'])

    def test_get(self):
        doc_id = self.documents[0].id
        ref_id = self.documents[0].ref.id
        response = requests.get(self.base_url, params={'id': doc_id})
        response.connection.close()
        self.assertEqual(response.json()['ref']['id'], str(ref_id))

    def test_list(self):
        ref = self.relateds[1]
        params = {'ref_id': ref.id}
        response = requests.get(self.base_url + 'list',
                                params=params)
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 4)

    def test_delete(self):
        doc_id = self.documents[0].id
        response = requests.delete(self.base_url,
                                   params={'id': doc_id})
        response.connection.close()
        response = requests.get(self.base_url + 'list')
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 9)

