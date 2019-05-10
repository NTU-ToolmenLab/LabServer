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

    def not_found(self, rep):
        self.assertEqual(rep.status_code, 404)
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

    def test_basic(self):
        rep = get(self.url)
        self.not_found(rep)

    def test_basic_error(self):
        rep = get(self.url + '/hi')
        self.not_found(rep)

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
        self.not_found(rep)

    def test_basic_search_fail_image(self):
        rep = post(self.url + '/searchimage', data={'name': name})
        self.not_found(rep)

    def test_prune(self):
        rep = post(self.url + '/prune')
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertEqual(rep['status'], 200)
        self.assertEqual(rep['message'], 'ok')

    def test_delete_empty(self):
        rep = post(self.url + '/deleteImage', data={'name': name})
        self.not_found(rep)
        rep = post(self.url + '/delete', data={'name': name})
        self.not_found(rep)


class TestAPI_continue(unittest.TestCase):
    def setUp(self):
        self.url = url

    def checkOK(self, rep):
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertEqual(rep['status'], 200)
        self.assertEqual(rep['message'], 'ok')

    def test_create(self):
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
        self.checkOK(rep)

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
        self.checkOK(rep)
        con = client.containers.get(name)
        self.assertEqual(con.status, 'exited')

        # start
        print('Resume')
        rep = post(self.url + '/start', data={'name': name})
        self.checkOK(rep)
        con = client.containers.get(name)
        self.assertEqual(con.status, 'running')

        # change pw
        print('Change Password')
        con.exec_run('adduser ubuntu')
        rep = post(self.url + '/passwd', data={'name': name,
                                               'pw': 'tmpPW'})
        self.checkOK(rep)
        self.assertIn('tmpPW', con.exec_run('cat /etc/shadow').output.decode())

        # commit
        print('Commit')
        rep = post(self.url + '/commit', data={'name': name,
                                               'newname': name})
        self.checkOK(rep)

        # search image
        rep = post(self.url + '/searchimage', data={'name': name})
        rep = rep.json()
        self.assertIsInstance(rep, dict)

        # delete
        print('Delete')
        rep = post(self.url + '/delete', data={'name': name})
        self.checkOK(rep)

        # exit
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

        # Delete Image
        print('Delete Image')
        rep = post(self.url + '/deleteImage', data={'name': name})
        self.checkOK(rep)

        # Check if delete it
        rep = post(self.url + '/searchimage', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)


    def test_double_create(self):
        os.makedirs('/home/nas/tmp0', exist_ok=True)
        os.makedirs('/nashome/guest/test/tmp1', exist_ok=True)

        print('Create')
        rep = post(self.url + '/create', data={
            'image': 'nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04',
            'homepath': 'guest/test',
            'labnas': False,
            'name': 'unit_test'})
        self.checkOK(rep)

        con = client.containers.get(name)
        self.assertNotIn('tmp0', con.exec_run('ls /home/nas').output.decode())

        rep = post(self.url + '/create', data={
            'image': 'nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04',
            'homepath': 'guest/test',
            'labnas': False,
            'name': 'unit_test'})
        self.assertEqual(rep.status_code, 403)
        rep = rep.json()
        self.assertEqual(rep['status'], 403)

        print('Delete')
        rep = post(self.url + '/delete', data={'name': name})
        self.checkOK(rep)


if __name__ == '__main__':
    unittest.main()
