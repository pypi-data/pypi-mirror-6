#-*- coding: utf-8 -*-

# messy functional tests. Refactor needed.

import sys
import os
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

connection = MongoConnection(db_settings['NAME'],
                             host=db_settings['HOST'],
                             port=db_settings['PORT'])
connection.connect()


class SomeDoc(Document):
    attr = StringField()
    attr2 = IntField()


class OtherDoc(Document):
    ref = ReferenceField(SomeDoc)

application = Application([(r'/somedoc/(.*)', RestHandler,
                            dict(model=SomeDoc)),
                           (r'/otherdoc/(.*)', RestHandler,
                            dict(model=OtherDoc))])


class AutoAPITestCase(TornadoApplicationTestCase):
    @classmethod
    def setUpClass(cls):
        cls.python_exec = cls._get_python_exec()
        cls.application = 'functional_tests.test_autoapi.application'
        super(AutoAPITestCase, cls).setUpClass()

    def setUp(self):
        self.somedoc1 = SomeDoc(attr='asfd', attr2=1)
        self.somedoc1.save()
        self.somedoc2 = SomeDoc(attr='qwre', attr2=2)
        self.somedoc2.save()
        self.ref1 = OtherDoc(ref=self.somedoc1)
        self.ref1.save()
        self.ref2 = OtherDoc(ref=self.somedoc1)
        self.ref2.save()

        self.ref3 = OtherDoc(ref=self.somedoc2)
        self.ref3.save()

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

    def tearDown(self):
        OtherDoc.drop_collection()
        SomeDoc.drop_collection()

    def test_list(self):
        url = 'http://localhost:8888/somedoc/list'
        response = requests.get(url)
        response.connection.close()
        self.assertEqual(len(response.json()), 2)

    def test_list_with_filter(self):
        url = 'http://localhost:8888/otherdoc/list'
        response = requests.get(url, params={'ref_id': self.somedoc1.id})
        response.connection.close()
        self.assertEqual(len(response.json()), 2)

    def test_get(self):
        url = 'http://localhost:8888/somedoc/'
        response = requests.get(url, params={'id': self.somedoc1.id})
        response.connection.close()
        self.assertEqual(response.json()['id'], str(self.somedoc1.id))

    def test_delete(self):
        url = 'http://localhost:8888/somedoc/'
        response = requests.delete(url, params={'id': self.somedoc1.id})
        response.connection.close()
        response = requests.get(url + 'list')
        response.connection.close()

        self.assertEqual(len(response.json()), 1)

    def test_put_new_object(self):
        url = 'http://localhost:8888/somedoc/'
        response = requests.put(url, params={'attr': 'bla', 'attr2': 2})
        response.connection.close()
        response = requests.get(url + 'list')
        response.connection.close()

        self.assertEqual(len(response.json()), 3)

    def test_put_updata_object(self):
        url = 'http://localhost:8888/somedoc/'
        response = requests.put(url, params={'id': self.somedoc2.id,
                                             'attr2': 20})
        response.connection.close()
        response = requests.get(url + 'list')
        response.connection.close()

        self.assertEqual(len(response.json()), 2)
