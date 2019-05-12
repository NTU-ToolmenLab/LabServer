import unittest
from requests import get, post, Session
import os
import time
from lxml import html
import sqlite3
import paramiko
from config import config


url = 'http://localhost:5000'
ssh_host = config['domain_name']
ssh_port = 22
web_port = 443
name = 'guest'
password = 'password'
test_node = 'lab304-server3'
test_node1 = 'lab304-server1'
image_name = 'learn3.6'
box_name = 'tmp1'
conn = sqlite3.connect('/app/db.sqlite')
user_xpath = '//div[contains(@class, "card-footer")]/text()'
login_str = '<a class="navbar-brand"> ' + name + ' </a>'


def get_ssh(self, password=password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_host,
                   port=ssh_port,
                   allow_agent=False,
                   username=name + '_' + box_name,
                   password=password)
    return client


class Test_login(unittest.TestCase):
    def setUp(self):
        self.url = url

    def isLoginPage(self, func, url):
        rep = func(self.url + url)
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Welcome to ', rep.text)

    def is_401(self, func, url):
        rep = func(self.url + url)
        self.assertEqual(rep.status_code, 401)

    def test_basic(self):
        self.isLoginPage(get, '')

    def test_not_found(self):
        rep = get(self.url + '/12345')
        self.assertEqual(rep.status_code, 404)

    def test_not_correct_method(self):
        rep = get(self.url + '/box/api')
        self.assertEqual(rep.status_code, 405)

    def test_not_auth(self):
        self.isLoginPage(post, '/box')
        self.isLoginPage(post, '/box/api')
        self.isLoginPage(post, '/box/create')
        self.isLoginPage(post, '/box/vnctoken')
        self.isLoginPage(get, '/oauth/authorize')
        self.isLoginPage(get, '/oauth/client')
        self.isLoginPage(post, '/oauth/client')
        self.isLoginPage(get, '/adminpage')
        self.isLoginPage(post, '/adminpage')
        self.isLoginPage(get, '/passwd')
        self.isLoginPage(post, '/passwd')
        self.isLoginPage(get, '/logout')
        self.isLoginPage(get, '/help')

    def test_no_login(self):
        rep = get(self.url + '/box')
        self.assertIn('Welcome to ', rep.text)
        self.assertIn('?next=%2Fbox%2F', rep.url)

    def test_login_fail(self):
        rep = post(self.url, data={
            'username': name,
            'password': '123123123'})
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Fail to Login', rep.text)

        rep = post(self.url, data={
            'password': '123123123'})
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Fail to Login', rep.text)

        rep = post(self.url, data={
            'username': name})
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Fail to Login', rep.text)

    def test_login_ok(self):
        rep = post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)
        self.assertIn(login_str, rep.text)

    def test_not_auth(self):
        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (0, name))
        conn.commit()
        s = Session()
        rep = s.post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)

        self.is_401(s.get, '/oauth/client')
        self.is_401(s.post, '/oauth/client')
        self.is_401(s.get, '/adminpage')
        self.is_401(s.post, '/adminpage')

    def test_not_auth_other_group(self):
        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (2, name))
        conn.commit()
        s = Session()
        rep = s.post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)

        self.is_401(s.get, '/oauth/client')
        self.is_401(s.post, '/oauth/client')
        self.is_401(s.get, '/adminpage')
        self.is_401(s.post, '/adminpage')

    def test_logout(self):
        s = Session()
        rep = s.post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)
        self.isLoginPage(s.get, '/logout')
        self.isLoginPage(s.get, '/box')

    def test_vnctoken(self):
        s = Session()
        rep = s.post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)
        rep = s.post(self.url + '/box/vnctoken')
        self.assertEqual(rep.status_code, 403)


class Test_admin(unittest.TestCase):
    # TODO test /oauth/client and /adminpage
    def setUp(self):
        self.url = url

    def is_access(self, func, url):
        rep = func(self.url + url)
        self.assertEqual(rep.status_code, 200)
        self.assertEqual(rep.url, self.url + url)

    def test_db(self):
        res = conn.execute('SELECT * FROM user WHERE name = ?', (name,))
        self.assertTrue(res.fetchall())

    def test_admin(self):
        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (1, name))
        conn.commit()

        s = Session()
        rep = s.post(self.url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)

        self.is_access(s.get, '/oauth/client')
        self.is_access(s.get, '/adminpage')

        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (0, name))
        conn.commit()


class Test_api(unittest.TestCase):
    def setUp(self):
        self.url = url + '/box/'
        self.s = Session()
        rep = self.s.post(url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)

    def connect_ssh(self):
        time.sleep(5)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ssh_host,
                       port=ssh_port,
                       allow_agent=False,
                       username=name + '_' + box_name,
                       password=password)
        return client

    def get_realname(self):
        rep = self.s.get(self.url)
        tree = html.fromstring(rep.content)
        realname = tree.xpath(user_xpath)
        return realname

    def chect_num(self, num):
        rep = self.s.get(self.url)
        self.assertIn(str(num + 1) + '/3', rep.text)
        self.assertEqual(num, len(self.get_realname()))

    def wait(self, status):
        t = 30
        while t > 0:
            rep = self.s.get(self.url)
            if status in rep.text:
                break
            t -= 1
            print('.')
            time.sleep(3)
        else:
            self.assertTrue(False)

    def test_cycle(self):
        self.chect_num(0)

        # check No other boxes
        print('Create')
        rep = self.s.post(self.url + 'create', data={
            'name': box_name,
            'node': test_node,
            'image': image_name})
        self.assertEqual(rep.status_code, 200)

        print('Wait for creation')
        self.wait('status: running')
        self.chect_num(1)

        # check
        realname = self.get_realname()[0].strip()
        client = self.connect_ssh()
        sudo = 'echo ' + password + ' | sudo -S '
        _, stdout, _ = client.exec_command('ls /home')
        self.assertNotIn('tmp2\n', stdout.readlines())
        _, stdout, _ = client.exec_command(sudo + 'mkdir /home/tmp2')
        time.sleep(1)

        print('Restart')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Restart',
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        # check
        time.sleep(3)
        client = self.connect_ssh()
        _, stdout, _ = client.exec_command('ls /home')
        self.assertIn('tmp2\n', stdout.readlines())

        print('Rescue')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Rescue',
            'name': realname})
        self.assertEqual(rep.status_code, 200)
        time.sleep(3)

        print('Wait for rescue')
        self.wait('status: running')
        self.chect_num(1)

        # check
        client = self.connect_ssh()
        _, stdout, _ = client.exec_command('ls /home')
        self.assertNotIn('tmp2\n', stdout.readlines())
        client.exec_command(sudo + 'mkdir /home/tmp2')
        time.sleep(1)

        print('Stop')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Stop',
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        print('Wait for stoping')
        self.wait('status: 404')
        self.chect_num(1)

        print('Rescue Stop')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Rescue',
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        print('Wait for rescuing stopped')
        self.wait('status: running')
        self.chect_num(1)

        # check
        client = self.connect_ssh()
        _, stdout, _ = client.exec_command('ls /home')
        self.assertIn('tmp2\n', stdout.readlines())
        client.exec_command(sudo + 'mkdir /home/tmp3')
        time.sleep(1)

        print('Change Node')
        rep = self.s.post(self.url + 'api', data={
            'method': 'node',
            'node': test_node1,
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        print('Wait for chaning node')
        self.wait('status: running')
        self.chect_num(1)

        # check
        client = self.connect_ssh()
        _, stdout, _ = client.exec_command('ls /home')
        self.assertIn('tmp3\n', stdout.readlines())

        print('Delete')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Delete',
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        print('Wait for deletion')
        self.wait('1/3')
        self.chect_num(0)

    def test_wrong_name(self):
        rep = self.s.post(self.url + 'api')
        self.assertEqual(rep.status_code, 403)

        rep = self.s.post(self.url + 'api', data={
            'name': '123123'})
        self.assertEqual(rep.status_code, 403)

        rep = self.s.post(self.url + 'api', data={
            'method': 'Restart',
            'name': '123123'})
        self.assertEqual(rep.status_code, 403)

        rep = self.s.post(self.url + 'api', data={
            'method': 'Restart'})
        self.assertEqual(rep.status_code, 403)

    def test_create_rule(self):
        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (2, name))
        conn.commit()

        print('Create')
        rep = self.s.post(self.url + 'create', data={
            'name': box_name,
            'node': test_node1,
            'image': image_name})
        self.assertEqual(rep.status_code, 200)
        print('Wait for creation')
        self.wait('status: running')

        # check
        realname = self.get_realname()[0].strip()
        client = self.connect_ssh()
        _, stdout, _ = client.exec_command('ls /home/nas')
        self.assertNotIn('tmp0\n', stdout.readlines())

        rep = self.s.get(self.url)
        self.assertIn('selected> ' + test_node, rep.text)

        print('Delete')
        rep = self.s.post(self.url + 'api', data={
            'method': 'Delete',
            'name': realname})
        self.assertEqual(rep.status_code, 200)

        print('Wait for deletion')
        self.wait('1/3')

        conn.execute('UPDATE user SET groupid = ? WHERE name = ?', (0, name))
        conn.commit()


# TODO: tearDown manually
class Test_after_create(unittest.TestCase):
    def setUp(self):
        self.url = url + '/box/'
        self.s = Session()
        rep = self.s.post(url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)

        # create one if not exist
        rep = self.s.get(self.url)
        if '1/3' not in rep.text:
            return
        self.assertIn('1/3', rep.text)

        rep = self.s.post(self.url + 'create', data={
            'name': box_name,
            'node': test_node,
            'image': image_name})
        self.assertEqual(rep.status_code, 200)

        time.sleep(3)
        rep = self.s.get(self.url)
        self.assertIn('2/3', rep.text)

        print('Wait for creation')
        t = 10
        while t > 0:
            rep = self.s.get(self.url)
            if 'status: running' in rep.text:
                break
            t -= 1
            print('.')
            time.sleep(3)
        else:
            self.assertTrue(False)

    def test_double_create(self):
        rep = self.s.post(self.url + 'create', data={
            'name': box_name,
            'node': test_node,
            'image': image_name})
        self.assertEqual(rep.status_code, 403)

        rep = self.s.get(self.url)
        self.assertIn('2/3', rep.text)

    def test_wrong_create(self):
        rep = self.s.post(self.url + 'create', data={
            'node': test_node,
            'image': '123123123'})
        self.assertEqual(rep.status_code, 403)

        rep = self.s.post(self.url + 'create', data={
            'node': '123123',
            'image': image_name})
        self.assertEqual(rep.status_code, 403)

        rep = self.s.post(self.url + 'create', data={
            'name': 'ZZZ',
            'node': test_node,
            'image': image_name})
        self.assertEqual(rep.status_code, 403)

    def test_jupyter(self):
        # get id
        rep = self.s.get(self.url)
        tree = html.fromstring(rep.content)
        realname = tree.xpath(user_xpath)
        realname = realname[0].strip()

        # test jupyter
        rep = get(f'https://{ssh_host}:{web_port}/jupyter/{realname}')
        self.assertEqual(rep.status_code, 200)

    def test_vnc(self):
        # TODO vnc is hard to test
        pass

    def test_ssh(self):
        client = get_ssh()

        # test sync folder
        _, stdout, _ = client.exec_command('ls /home/nas')
        self.assertIn('tmp0\n', stdout.readlines())
        _, stdout, _ = client.exec_command('ls /home/ubuntu')
        self.assertIn('tmp1\n', stdout.readlines())
        # test sudo
        _, stdout, _ = client.exec_command('echo ' + password + ' | sudo -S echo 123')
        self.assertIn('123\n', stdout.readlines())

    def get_realname(self):
        rep = self.s.get(self.url)
        tree = html.fromstring(rep.content)
        realname = tree.xpath(user_xpath)
        return realname[0].strip()

    def test_wrong_node(self):
        rep = self.s.post(self.url + 'api', data={
            'method': 'node',
            'node': '123123',
            'name': self.get_realname()})

    def test_excess_quota(self):
        conn.execute('UPDATE user SET quota = ? WHERE name = ?', (1, name))
        conn.commit()

        rep = self.s.post(self.url + 'create', data={
            'name': 'tmp2',
            'node': test_node,
            'image': image_name})
        self.assertEqual(rep.status_code, 403)

        conn.execute('UPDATE user SET quota = ? WHERE name = ?', (3, name))
        conn.commit()

    def test_access_other_fail(self):
        bn = name + '_' + box_name
        realname = self.get_realname()
        conn.execute('UPDATE box SET user = ? WHERE box_name = ?', ('123', bn))
        conn.commit()

        rep = self.s.post(self.url + 'api', data={
            'method': 'Delete',
            'name': realname})
        self.assertEqual(rep.status_code, 403)

        conn.execute('UPDATE box SET user = ? WHERE box_name = ?', (name, bn))
        conn.commit()

    def is_passwd_not_ok(self, data):
        rep = self.s.post(url + '/passwd', data=data)
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Reset Password', rep.text)

    def test_passwd_fail(self):
        # too short
        self.is_passwd_not_ok({
            'opw': password,
            'npw': '123',
            'npw1': '123',
        })

        # too long
        self.is_passwd_not_ok({
            'opw': password,
            'npw': '123' * 100,
            'npw1': '123' * 100,
        })

        # wrong old
        self.is_passwd_not_ok({
            'opw': '123123',
            'npw': '123123123',
            'npw1': '123123123',
        })

        # inconsist
        self.is_passwd_not_ok({
            'opw': password,
            'npw': '123123123',
            'npw1': '123',
        })

    def test_passwd_good(self):
        # change it
        password1 = password + '1'
        rep = self.s.post(url + '/passwd', data={
            'opw': password,
            'npw': password1,
            'npw1': password1,
        })
        self.assertEqual(rep.status_code, 200)
        self.assertIn(login_str, rep.text)

        # cannot login
        rep = post(url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)
        self.assertIn('Fail to Login', rep.text)

        # can login
        rep = post(url, data={
            'username': name,
            'password': password1})
        self.assertEqual(rep.status_code, 200)
        self.assertIn(login_str, rep.text)

        # can login with ssh
        get_ssh(password1)

        # change back
        rep = self.s.post(url + '/passwd', data={
            'opw': password1,
            'npw': password,
            'npw1': password,
        })

        # check
        rep = self.s.post(url, data={
            'username': name,
            'password': password})
        self.assertEqual(rep.status_code, 200)
        self.assertIn(login_str, rep.text)

    def test_vnctoken(self):
        rep = self.s.post(self.url + 'vnctoken', data={
            'token': self.get_realname()})
        self.assertEqual(rep.status_code, 200)
        self.assertEqual(rep.text, config['vnc_password'])


if __name__ == '__main__':
    unittest.main()
