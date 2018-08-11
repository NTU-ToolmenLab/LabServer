from flask_testing import TestCase
import unittest
from flask import Flask
from models import User, db, add_user
import requests
import passlib.hash
from lxml import etree
import datetime
import time

class TestDB(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': "sqlite:////tmp/db.sqlite1",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        db.init_app(app)
        return app

    @classmethod
    def setUpClass(cls):
        cls.password = passlib.hash.sha512_crypt.hash('test123')

    def setUp(self):
        db.drop_all()
        db.create_all()
        user = User(name="test", password=self.password, admin=0)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add(self):
        user = User(name="test1", password="test123", admin=0)
        db.session.add(user)
        self.assertEqual(len(User.query.all()), 2)

        a = User.query.filter_by(name='test1').first()
        self.assertEqual(a.name, 'test1')
        self.assertEqual(a.password, 'test123')
        self.assertEqual(a.admin, False)

        db.session.remove()
        self.assertEqual(len(User.query.all()), 1)

    def test_found(self):
        a = User.query.filter_by(name='test').first()
        self.assertTrue(a.checkPassword("test123"))

    def test_not_found(self):
        a = User.query.filter_by(name='test2').first()
        self.assertEqual(a, None)

    def test_get_key(self):
        a = User.query.filter_by(name='test').first()
        # import pdb
        # pdb.set_trace()
        d = dict(a.__dict__)
        di = {k: v for k, v in d.items() if not k.startswith('_')}

        it = User.__table__.columns.items()
        it[0][1].type.python_type

    def test_get_key(self):
        a = User.query.filter_by(name='test').first()
        # import pdb
        # pdb.set_trace()
        d = dict(a.__dict__)
        di = {k: v for k, v in d.items() if not k.startswith('_')}

        it = User.__table__.columns.items()
        it[0][1].type.python_type

    def test_get_key(self):
        a = User.query.filter_by(name='test').first()
        a.passtime = time.time()

class Test_Login(unittest.TestCase):
    def test_look_error(self):
        a = requests.get("http://127.0.0.1:5000/api/hi")
        self.assertEqual(a.status_code, 401)

    def test_look(self):
        a = requests.get("http://127.0.0.1:5000")
        self.assertTrue(a.ok)
        self.assertTrue("Welcom" in a.text)

    def test_login(self):
        a = requests.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        self.assertTrue(a.ok)
        self.assertEqual(a.json(), {'hi': True})

    def test_not_login(self):
        a = requests.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'testWrong'})
        self.assertTrue(a.ok)
        self.assertTrue("Fail to Login" in a.text)


class Test_passwd(unittest.TestCase):
    def test_passwd_0(self):
        a = requests.get("http://127.0.0.1:5000/passwd")
        self.assertEqual(a.status_code, 401)

    def test_passwd(self):
        s = requests.Session()
        a = s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        self.assertTrue(a.ok)
        self.assertEqual(a.json(), {'hi': True})
        a = s.get("http://127.0.0.1:5000/passwd")
        self.assertTrue(a.ok)

    def test_passwd_1(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test',
                'npw': 'test123123xx',
                'npw1': 'test123123'})
        self.assertTrue(a.ok)
        self.assertTrue("confirm password error" in a.text)

    def test_passwd_2(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test',
                'npw': 'test123123',
                'npw1': 'test123123'})
        self.assertTrue(a.ok)
        self.assertTrue("Wrong password" in a.text)

    def test_passwd_3(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test123',
                'npw': 'test',
                'npw1': 'test'})
        self.assertTrue(a.ok)
        self.assertTrue("Password should be more than 8 characters" in a.text)

    def test_passwd_4(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test_user',
            'userPassword': 'test123123'})
        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test123123',
                'npw': 'test1231234',
                'npw1': 'test1231234'})
        self.assertTrue(a.ok)
        self.assertEqual(a.json(), {'hi': True})

    def test_passwd_5(self):
        s = requests.Session()
        a = s.post("http://127.0.0.1:5000", data={
            'userName': 'test_user',
            'userPassword': 'test1231234'})
        self.assertTrue(a.ok)
        self.assertEqual(a.json(), {'hi': True})

        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test1231234',
                'npw': 'test123123',
                'npw1': 'test123123'})
        self.assertTrue(a.ok)

class Test_lists(unittest.TestCase):
    def test_nologin(self):
        a = requests.get("http://127.0.0.1:5000/box/list")
        self.assertEqual(a.status_code, 401)

    def test_list(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.get("http://127.0.0.1:5000/box/list")
        self.assertTrue(a.ok)

    def test_logout(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.get("http://127.0.0.1:5000/logout")
        self.assertTrue("Welcome" in a.text)

        a = requests.get("http://127.0.0.1:5000/api/hi")
        self.assertEqual(a.status_code, 401)
        
    def test_glabol(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.get("http://127.0.0.1:5000/box/list")
        self.assertTrue("127.0.0.1" in a.text)


class Test_adminpage(unittest.TestCase):
    def test_nologin(self):
        a = requests.get("http://127.0.0.1:5000/box/list")
        self.assertEqual(a.status_code, 401)
        
    def test_nologin(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test_user',
            'userPassword': 'test123123'})
        a = s.get("http://127.0.0.1:5000/adminpage")
        self.assertEqual(a.status_code, 401)

    def test_login(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.get("http://127.0.0.1:5000/adminpage")
        self.assertTrue(a.ok)

    def test_update_1(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/adminpage", data={
            'admin'   : 0,
            'id'      : 5,
            'method'  : 'add',
            'name'    : 'x',
            'password': 'x',
            'passtime': 0,
            'table'   : 'login'})
        self.assertTrue(a.ok)

    def test_update_2(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/adminpage", data={
            'admin'   : 0,
            'id'      : 5,
            'method'  : 'add',
            'name'    : 'xx',
            'password': 'x',
            'passtime': 0,
            'table'   : 'login'})
        self.assertTrue(a.ok)


    def test_update_3(self):
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test',
            'userPassword': 'test123'})
        a = s.post("http://127.0.0.1:5000/adminpage", data={
            'admin'   : 0,
            'id'      : 5,
            'method'  : 'delete',
            'name'    : 'x',
            'password': 'x',
            'passtime': 0,
            'table'   : 'login'})
        self.assertTrue(a.ok)

class TestRealDB(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': "sqlite:////tmp/db.sqlite",
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        })
        db.init_app(app)
        return app

    def test_add_user(self):
        user = add_user(name='test1', passwd='test1')
        self.assertTrue(User.query.filter_by(name='test1'))

    def test_passtime(self):
        User.query.filter_by(name='test_user').first().passtime = 0 
        db.session.commit()
        s = requests.Session()
        s.post("http://127.0.0.1:5000", data={
            'userName': 'test_user',
            'userPassword': 'test123123'})
        a = s.post("http://127.0.0.1:5000/passwd", data={
                'opw': 'test123123',
                'npw': 'test123123',
                'npw1': 'test123123'})
        a = User.query.filter_by(name='test_user').first()
        self.assertTrue(a.passtime > 1)
        a.passtime = 0.0
        db.session.commit()

    def test_add_user(self):
        add_user(name='test1', passwd='test1')
        a = User.query.filter_by(name='test1').first()
        self.assertTrue(a)
        db.session.delete(a)
        db.session.commit()

    def test_readd_user(self):
        with self.assertRaises(AssertionError):
            user = add_user(name='test', passwd='test123')

if __name__ == '__main__':
    unittest.main()
