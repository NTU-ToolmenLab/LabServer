from flask_testing import TestCase
import unittest
from flask import Flask
from models import User, db
import requests
import passlib.hash

class TestAll(TestCase):
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

    # DB
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

    # Login
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
        

if __name__ == '__main__':
    unittest.main()
