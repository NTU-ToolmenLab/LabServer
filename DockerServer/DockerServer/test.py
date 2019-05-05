import unittest
import docker
from requests import get, post
import os
import time


client = docker.from_env()
url = 'http://localhost:3476'
name = 'unit_test'


class TestDocker(unittest.TestCase):
    def test_basic(self):
        envs = client.containers.list()
        self.assertGreater(len(envs), 0)


class TestAPI_unit(unittest.TestCase):
    def setUp(self):
        self.url = url

    def test_basic(self):
        rep = get(self.url)
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

    def test_basic_error(self):
        rep = get(self.url + '/hi')
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

    def test_basic_405(self):
        rep = get(self.url + '/search')
        self.assertEqual(rep.status_code, 405)

    def test_basic_search(self):
        rep = post(self.url + '/search')
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertIsInstance(rep, list)
        self.assertIsInstance(rep[0], dict)

    def test_basic_search_fail(self):
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

    def test_basic_search_fail_image(self):
        rep = post(self.url + '/searchimage', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

    def test_prune(self):
        rep = post(self.url + '/prune')
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertEqual(rep['status'], 200)
        self.assertEqual(rep['message'], 'ok')


class TestAPI_continue(unittest.TestCase):
    def setUp(self):
        self.url = url

    def test_create(self):
        def checkOK(rep):
            self.assertEqual(rep.status_code, 200)
            rep = rep.json()
            self.assertEqual(rep['status'], 200)
            self.assertEqual(rep['message'], 'ok')

        # Before Create
        print('Create')
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

        os.makedirs('/home/nas/tmp0', exist_ok=True)
        os.makedirs('/nashome/guest/test/tmp1', exist_ok=True)

        # Create
        rep = post(self.url + '/create', data={
            'image': 'nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04',
            'homepath': 'guest/test',
            'labnas': True,
            'name': 'unit_test'})
        checkOK(rep)

        # Check Created
        print('Check Create and Mount')
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertIsInstance(rep, dict)
        self.assertEqual(rep['status'], 'running')

        # Check Share Dir
        con = client.containers.get(name)
        self.assertIn('tmp0', con.exec_run('ls /home/nas').output.decode())
        self.assertIn('tmp1', con.exec_run('ls /home/ubuntu').output.decode())
        # check container
        self.assertEqual(con.status, 'running')

        # Stop
        print('Stop')
        rep = post(self.url + '/stop', data={'name': name})
        checkOK(rep)
        con = client.containers.get(name)
        self.assertEqual(con.status, 'exited')

        # start
        print('Resume')
        rep = post(self.url + '/start', data={'name': name})
        checkOK(rep)
        con = client.containers.get(name)
        self.assertEqual(con.status, 'running')

        # change pw
        print('Change Password')
        con.exec_run('adduser ubuntu')
        rep = post(self.url + '/passwd', data={'name': name,
                                               'pw': 'tmpPW'})
        checkOK(rep)
        self.assertIn('tmpPW', con.exec_run('cat /etc/shadow').output.decode())

        # commit
        print('Commit')
        rep = post(self.url + '/commit', data={'name': name,
                                               'newname': name})
        checkOK(rep)

        # search image
        rep = post(self.url + '/searchimage', data={'name': name})
        rep = rep.json()
        self.assertIsInstance(rep, dict)

        # delete
        print('Delete')
        rep = post(self.url + '/delete', data={'name': name})
        checkOK(rep)

        # exit
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

        # Delete Image
        print('Delete Image')
        rep = post(self.url + '/deleteImage', data={'name': name})
        checkOK(rep)

        # Check if delete it
        rep = post(self.url + '/searchimage', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)


if __name__ == '__main__':
    unittest.main()
