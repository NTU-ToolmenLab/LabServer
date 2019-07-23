import unittest
from kubernetes import client, config, stream
from requests import get, post
import os
import time
import yaml


config.load_incluster_config()
v1 = client.CoreV1Api()
v1beta = client.ExtensionsV1beta1Api()
url = 'http://localhost:3476'
name = 'unit-test'
test_node = 'lab304-server3'
ns = 'user'
image_name = 'harbor.default.svc.cluster.local/linnil1/serverbox:learn3.6'


class Test_K8s(unittest.TestCase):
    def test_basic(self):
        pods = v1.list_pod_for_all_namespaces(watch=False)
        self.assertGreater(len(pods.items), 0)


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

    def test_listnode(self):
        rep = post(self.url + '/listnode')
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertIsInstance(rep, list)
        self.assertIsInstance(rep[0], dict)
        self.assertIn('ip', rep[0])
        self.assertIn('name', rep[0])
        return rep

    def test_basic_search_fail(self):
        rep = post(self.url + '/search', data={'name': name})
        self.not_found(rep)

    def test_send_node(self):
        rep = self.test_listnode()
        for node in rep:
            rep = post(self.url + '/' + node['name'] + '/search')
            self.assertEqual(rep.status_code, 200)
            rep = rep.json()
            self.assertIsInstance(rep, list)
            self.assertIsInstance(rep[0], dict)

    def test_delete_empty(self):
        rep = post(self.url + '/delete', data={'name': name})
        self.not_found(rep)

    def test_bad_node(self):
        rep = post(self.url + '/create', data={
            'image': image_name,
            'homepath': 'guest/test',
            'labnas': True,
            'node': '123123123123',
            'name': name})
        self.not_found(rep)

    def test_redir_node_error(self):
        rep = post(self.url + '/123123/search')
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
        ''' run this after you create testing folder in here:
        * /home/nas/tmp0
        * /nashome/guest/test/tmp1
        '''

        os.makedirs('/home/nas/tmp0', exist_ok=True)
        os.makedirs('/nashome/guest/test/tmp1', exist_ok=True)

        # Before Create
        print('Check before Creation')
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)
        with self.assertRaises(client.rest.ApiException):
            v1.read_namespaced_service(name, ns)
        with self.assertRaises(client.rest.ApiException):
            v1beta.read_namespaced_ingress(name, ns)

        # Create
        print('Wait for Creation')
        rep = post(self.url + '/create', data={
            'image': image_name,
            'homepath': 'guest/test',
            'labnas': True,
            'node': test_node,
            'name': name})
        self.checkOK(rep)

        # Wait
        t = 20
        while t > 0:
            print('.')
            rep = post(self.url + '/search', data={'name': name})
            rep = rep.json()
            if rep['status'] == 'Running':
                break
            t = t - 1
            time.sleep(3)
        else:
            self.assertTrue(False)

        # checking
        print('Checking pods service ingress')
        # no raise
        v1.read_namespaced_service(name, ns)
        v1beta.read_namespaced_ingress(name, ns)

        # Check Share Dir
        resp = stream.stream(v1.connect_get_namespaced_pod_exec, name, ns,
                             command=["ls", "/home/nas"],
                             stderr=True, stdin=True, stdout=True, tty=False)
        self.assertIn('tmp0', resp)
        resp = stream.stream(v1.connect_get_namespaced_pod_exec, name, ns,
                             command=["ls", "/home/ubuntu"],
                             stderr=True, stdin=True, stdout=True, tty=False)
        self.assertIn('tmp1', resp)

        # Delete
        print('Wait for Deletion')
        rep = post(self.url + '/delete', data={'name': name})
        self.checkOK(rep)

        # Wait
        t = 30
        while t > 0:
            rep = post(self.url + '/search', data={'name': name})
            rep = rep.json()
            if rep['status'] == 404:
                break
            t = t - 1
            print('.')
            time.sleep(3)
        else:
            self.assertTrue(False)

        # Check if delete it
        print('Check for Deletion')
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

        with self.assertRaises(client.rest.ApiException):
            v1.read_namespaced_service(name, ns)
        with self.assertRaises(client.rest.ApiException):
            v1beta.read_namespaced_ingress(name, ns)

    def test_running_op(self):
        '''
        * double_create
        * ingress and service exist with same name before creation
        * ingress and service not exist with same name before deletion
        '''
        # Before Create
        print('Check before Creation')
        rep = post(self.url + '/search', data={'name': name})
        rep = rep.json()
        self.assertEqual(rep['status'], 404)

        # create ingress and service
        template_ingress = yaml.load(open('/app/pod_ingress.yml'))
        template_ingress['metadata']['name'] = name
        path = template_ingress['spec']['rules'][0]['http']['paths'][0]
        path['path'] = path['path'].replace('hostname', name)
        path['backend']['serviceName'] = name
        template_service = yaml.load(open('/app/pod_service.yml'))
        template_service['metadata']['name'] = name
        template_service['spec']['selector']['srvname'] = name
        v1.create_namespaced_service(ns, template_service)
        v1beta.create_namespaced_ingress(ns, template_ingress)

        # Create
        print('Wait for Creation')
        rep = post(self.url + '/create', data={
            'image': image_name,
            'homepath': 'guest/test',
            'labnas': False,
            'node': test_node,
            'name': name})
        self.checkOK(rep)

        # Wait
        t = 20
        while t > 0:
            print('.')
            rep = post(self.url + '/search', data={'name': name})
            rep = rep.json()
            if rep['status'] == 'Running':
                break
            t = t - 1
            time.sleep(3)
        else:
            self.assertTrue(False)

        # Assert
        resp = stream.stream(v1.connect_get_namespaced_pod_exec, name, ns,
                             command=["ls", "/home/nas"],
                             stderr=True, stdin=True, stdout=True, tty=False)
        self.assertNotIn('tmp0', resp)

        # Double Creation
        rep = post(self.url + '/create', data={
            'image': image_name,
            'homepath': 'guest/test',
            'labnas': False,
            'node': test_node,
            'name': name})
        self.assertEqual(rep.status_code, 403)
        rep = rep.json()
        self.assertEqual(rep['status'], 403)

        # Create empty delete
        v1.delete_namespaced_service(name, ns)
        v1beta.delete_namespaced_ingress(name, ns)

        # Delete
        print('Wait for Deletion')
        rep = post(self.url + '/delete', data={'name': name})
        self.checkOK(rep)

        # Wait
        t = 30
        while t > 0:
            rep = post(self.url + '/search', data={'name': name})
            rep = rep.json()
            if rep['status'] == 404:
                break
            t = t - 1
            print('.')
            time.sleep(3)
        else:
            self.assertTrue(False)


class Test_command(unittest.TestCase):
    def setUp(self):
        self.url = url

    def checkOK(self, rep):
        self.assertEqual(rep.status_code, 200)
        rep = rep.json()
        self.assertEqual(rep['status'], 200)
        self.assertEqual(rep['message'], 'ok')

    def test_command(self):
        post(self.url + '/delete', data={'name': name})
        rep = post(self.url + '/create', data={
            'image': image_name,
            'homepath': 'guest',
            'labnas': False,
            'node': test_node,
            'command': 'echo 123 && sleep 5 && >&2 echo error',
            'name': name})
        self.checkOK(rep)

        # Wait
        t = 40
        while t > 0:
            rep = post(self.url + '/log', data={'name': name}).json()
            print(rep)
            if rep['status'] in ['Succeeded', 'Failed']:
                break
            t = t - 1
            time.sleep(1)
        else:
            self.assertTrue(False)

        # completed
        rep = post(self.url + '/log', data={'name': name}).json()
        self.assertEqual(rep['log'], '123\nerror\n')

        # delete
        rep = post(self.url + '/delete', data={'name': name})
        self.checkOK(rep)


if __name__ == '__main__':
    unittest.main()
