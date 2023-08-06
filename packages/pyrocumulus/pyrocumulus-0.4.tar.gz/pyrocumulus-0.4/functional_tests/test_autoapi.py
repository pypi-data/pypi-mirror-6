# messy functional tests. Refactor needed.
# functional tests for the auto api feature.
# here some models are created, an auto restful api is
# configured an then we run tests on it

import sys
import os
import copy
import requests
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (StringField, ReferenceField, IntField,
                                EmbeddedDocumentField, ListField)
from pyrocumulus.web.applications import RestApplication
from pyrocumulus.conf import get_settings_module
from pyrocumulus.db import MongoConnection
from pyrocumulus.testing import TornadoApplicationTestCase


settings = get_settings_module()
db_settings = settings.DATABASE['default']

connection = MongoConnection(db_settings['db'],
                             host=db_settings['host'],
                             port=db_settings['port'])
connection.connect()

# mongoengine tutorial
class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class Comment(EmbeddedDocument):
    content = StringField()
    name = StringField(max_length=120)


class Post(Document):
    title = StringField(max_length=120, required=True)
    # reverse_delete_rule=CASCADE
    authors = ListField(ReferenceField(User, reverse_delete_rule=2))
    tags = ListField(StringField(max_length=30))
    comments = ListField(EmbeddedDocumentField(Comment))

    meta = {'allow_inheritance': True}


class TextPost(Post):
    content = StringField()


class ImagePost(Post):
    image_path = StringField()


class LinkPost(Post):
    link_url = StringField()


application = RestApplication(User, TextPost, LinkPost, ImagePost)

class BaseTestCase(TornadoApplicationTestCase):
    # exclude it from examples
    @classmethod
    def setUpClass(cls):
        cls.python_exec = cls._get_python_exec()
        cls.application = 'functional_tests.test_autoapi.application'
        super(BaseTestCase, cls).setUpClass()

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


class UserAPITestCase(BaseTestCase):
    def setUp(self):
        self.base_url = 'http://localhost:%s/api/user/' % (
            settings.TORNADO_PORT)
        self.populate_db()

    def populate_db(self):
        for i in range(3):
            email = 'user%s@email.com' % i
            first_name = 'user %s' % i
            last_name = 'da silva'
            user = User(email=email, first_name=first_name,
                        last_name=last_name)
            user.save()

    def tearDown(self):
        User.drop_collection()
        Post.drop_collection()

    def test_create(self):
        params = {'email': 'zeninguem@acre.nada', 'first_name': 'ze',
                  'last_name': 'ninguem'}
        response = requests.put(self.base_url, params)
        response.connection.close()
        self.assertTrue(response.json()['id'])

    def test_create_without_required_field(self):
        params = {'first_name': 'ze', 'last_name': 'ninguem'}
        response = requests.put(self.base_url, params)
        response.connection.close()
        self.assertEqual(response.status_code, 500)

    def test_get(self):
        email = 'user0@email.com'
        response = requests.get(self.base_url, params={'email': email})
        response.connection.close()

        self.assertEqual(response.json()['email'], email)

    def test_list(self):
        response = requests.get(self.base_url + 'list')
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 3)

    def test_list_with_pagination(self):
        response = requests.get(self.base_url + 'list',
                                params={'max': 2, 'page': 1})
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 2)

    def test_list_with_filter(self):
        response = requests.get(self.base_url + 'list',
                                params={'first_name': 'user 2'})
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 1)

    def test_delete(self):
        response = requests.delete(self.base_url,
                                   params={'email': 'user1@email.com'})
        response.connection.close()
        response = requests.get(self.base_url + 'list')
        response.connection.close()
        self.assertEqual(len(response.json()['items']), 2)

    def test_options(self):
        response = requests.options(self.base_url)
        response.connection.close()
        self.assertTrue(response.json()['corsEnabled'])


# by now, our basic functions are tested, let's try something
# better
class BloggingTestCase(BaseTestCase):
    def setUp(self):
        self.base_url = 'http://localhost:%s/api/textpost/' % (
            settings.TORNADO_PORT)
        self.comments_url = self.base_url + 'comments/'
        self.populate_db()

    def populate_db(self):
        self.users = [User(email='user0@email.com').save(),
                      User(email='user1@email.com').save()]

        self.posts = [
            TextPost(
                title='post 1', authors=[self.users[0]],
                tags=['tag', 'nice', 'bla'],
                content='Mussum ipsum cacilds, vidis litro abertis.').save(),
            TextPost(
                title='post 2', autors=self.users, tags=['tag', 'bla'],
                content='Mussum ipsum cacilds, vidis litro abertis.').save()]
        post = self.posts[1]
        for i in range(10):
            c = Comment(name='ze da silva %s' % i,
                        comment='Mussum ipsum cacilds, vidis litro abertis.')
            post.comments.append(c)
            post.save()

    def tearDown(self):
        Post.drop_collection()
        User.drop_collection()

    def test_create_post(self):
        params = {'title': 'post test', 'authors': [self.users[0].id],
                  'tags': ['bla', 'ble', 'bli'],
                  'content': 'Mussum ipsum cacilds, vidis litro abertis.'}
        response = requests.put(self.base_url, params=params)
        response.connection.close()
        returned_tags = response.json()['tags']
        self.assertEqual(returned_tags, ['bla', 'ble', 'bli'])

    def test_list_post_by_tag(self):
        params = {'tags': 'nice'}
        response = requests.get(self.base_url + 'list', params=params)
        response.connection.close()

        self.assertEqual(len(response.json()['items']), 1)

    def test_comment_on_post(self):
        parent_id = self.posts[0].id
        name = 'ze da silva'
        comment = 'Mussum ipsum cacilds, vidis litro abertis.'
        params = {'parent_id': parent_id, 'name': name, 'comment': comment}
        response = requests.put(self.comments_url, params=params)
        response.connection.close()
        response = requests.get(self.base_url, params={'id': parent_id})
        response.connection.close()

        self.assertEqual(len(response.json()['comments']), 1)

    def test_list_post_comments(self):
        parent_id = self.posts[1].id
        response = requests.get(self.comments_url + 'list',
                                params={'parent_id': parent_id})
        response.connection.close()

        self.assertEqual(response.json()['total_items'], 10)

    def test_list_post_comments_with_pagination(self):
        # pagination here is useless for the database, since all EmbeddedDocument's
        # always came in the queries' result, but it is useful for paginating
        # its display
        parent_id = self.posts[1].id
        response = requests.get(self.comments_url + 'list',
                                params={'parent_id': parent_id,
                                        'page': 2, 'max': 6})
        response.connection.close()

        self.assertEqual(len(response.json()['items']), 4)

    def test_get_response_as_jsonp(self):
        params = {'callback': 'callback'}
        response = requests.get(self.base_url + 'list', params=params)
        response.connection.close()
        self.assertTrue(response.text.startswith('callback('))

#         for i in range(10):
#             self.documents = []
#             doc = OtherDocument(attribute='ueba! %s' % i)
#             if i < 6:
#                 doc.ref = self.relateds[0]
#             else:
#                 doc.ref = self.relateds[1]
#             doc.save()
#             self.documents.append(doc)

#     def tearDown(self):
#         MyFirstDocument.drop_collection()
#         OtherDocument.drop_collection()

#     def test_create(self):
#         response = requests.put(self.base_url, self.params)
#         response.connection.close()
#         self.assertTrue(response.json()['id'])

#     def test_get(self):
#         doc_id = self.documents[0].id
#         ref_id = self.documents[0].ref.id
#         response = requests.get(self.base_url, params={'id': doc_id})
#         response.connection.close()
#         self.assertEqual(response.json()['ref']['id'], str(ref_id))

#     def test_list(self):
#         ref = self.relateds[1]
#         params = {'ref_id': ref.id}
#         response = requests.get(self.base_url + 'list',
#                                 params=params)
#         response.connection.close()
#         self.assertEqual(len(response.json()['items']), 4)

#     def test_delete(self):
#         doc_id = self.documents[0].id
#         response = requests.delete(self.base_url,
#                                    params={'id': doc_id})
#         response.connection.close()
#         response = requests.get(self.base_url + 'list')
#         response.connection.close()
#         self.assertEqual(len(response.json()['items']), 9)
