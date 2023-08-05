import os
import unittest

from orm.api import Api


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.api = Api(os.environ['CONFINE_SERVER_API'])
    
    def test_attributes(self):
        self.assertEqual(['uri'], self.api._data.keys())
    
    def test_self_retrieve(self):
        self.api.retrieve()
        self.assertEqual(3, len(self.api._data))
    
    def test_managers(self):
        self.api.nodes
        with self.assertRaises(AttributeError):
            self.api.rata
    
    def test_login(self):
        self.assertRaises(self.api.ResponseStatusError, self.api.login)
        self.api.username = os.environ['CONFINE_USER']
        self.api.password = os.environ['CONFINE_PASSWORD']
        self.api.login()
        auth_header = self.api.DEFAULT_HEADERS['authorization']
        self.assertLess(20, auth_header)
    
    def test_login_providing_credentials(self):
        username = os.environ['CONFINE_USER']
        password = os.environ['CONFINE_PASSWORD']
        self.api.login(username=username, password=password)
        self.assertEqual(self.api.username, username)
        self.assertEqual(self.api.password, password)
        auth_header = self.api.DEFAULT_HEADERS['authorization']
        self.assertLess(20, auth_header)
    
    def test_logout(self):
        self.test_login()
        self.api.logout()
        self.assertNotIn('authorization', self.api.DEFAULT_HEADERS)
