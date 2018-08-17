# LabServer
Some application or dockerfiles run on server

## How to Build

### set python environment(Optional)
```
sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv env
source env/bin/active
```

### Create encrypt file

1. Use Lets Encrypt it!
**You should open port 80 for verification**

```
docker pull certbot/certbot
docker run --rm -it -p 80:80 -v $(pwd)/letsencrypt:/etc/letsencrypt certbot/certbot certonly --standalone
```

1.1. Renew it 

`docker run --rm -it -p 80:80 -p 443:443 -v $(pwd)/letsencrypt:/etc/letsencrypt certbot/certbot renew`

Then copy to `certs/`

`cp letsencrypt/live/my.domain.ntu.edu.tw/* certs/`

2. Do it Yourself
```
cd certs
openssl genrsa 1024 > privkey.pem
chmod 400 privkey.pem
openssl req -new -x509 -nodes -sha1 -days 365 -key privkey.pem -out fullchain.pem
cd ..
```

## Add traefik
docker pull traefik

## build OauthServer
```
cd LabServer/OauthServer
vim app.py # modify anythings in create_app
docker build . -t linnil1/oauthserver
docker run -it --rm -v $(pwd):/app/OauthServer linnil1/oauthserver flask initdb
```

## Add User and Container
1. Add it by command line
`docker run -it --rm -v $(pwd):/app/OauthServer linnil1/oauthserver flask std_add_user`
`docker run -it --rm -v $(pwd):/app/OauthServer linnil1/oauthserver flask std_add_box`

2. Add with code
Modify `std_add_user` in `app.py`, it is very easy.

3. Add it by web (After init)
If you are admin, go to `your.domain.name/adminpage` to modify.

4. You can add `help.html` in `oauthserver/templates/`
```
cd ..
```

## Control docker to start or stop
```
cd DockerServer
docker build . -t linnil1/dockerserver
cd ..
```

## Build VNC
```
cd my_vnc
git clone https://github.com/novnc/noVNC.git
cd noVNC
```

Build it by npm (I do it at another mechine).

```
npm install
./utils/use_require.js --with-app --as commonjs
mv build ../
cd ..
git clone https://github.com/novnc/websockify
cat token_plugin.py >> websockify/websockify/token_plugins.py
docker build . -t linnil1/docker-vnc
cd ..
```

## build example docker-firefox-vnc (for testing, Not require)
```
cd UserDocker
docker build . -t linnil1/docker-firefox
cd ..
```

## Build nextcloud
```
docker pull nextcloud:fpm
docker pull nginx
docker pull collabora/code
docker pull mariadb
cd Nextcloud
vim nginx.conf # modify server_name and error_page port
cd ..
```

## Modify docker-compose
`vim docker-compose.yml`

1. change host from 127.0.0.1 to my.domain
2. change port from 443 and 8888 if you want
3. nextcloud_db password
4. nextcloud external data path

## Finally, you can start your server
`docker-compose up -d`

## NextCloud

I provide two way to login NextCloud.
One is from
`my.domain.ntu.edu.tw:443/drive`
the other is
`my.domain.ntu.edu.tw:444`

It need to start to same containers because collabora cannot use in reverse proxy.

### init
edit `NextCloud/nextcloud/config/config.php`
```
  'trusted_domains' =>
  array (
    0 => 'my.domain.ntu.edu.tw:443',
    1 => 'my.domain.ntu.edu.tw:444',
  ),
  'overwritewebroot' => '/drive',
```

Go in to web https://my.domain.ntu.edu.tw:443/drive

Set admin and password, and choose mysql: hostname=nextclouddb, and the other are same as docker-compose written

enable "collabora" (Set https://my.domain.ntu.edu.tw:444)

### enable external storage
Add External Storage
```
cd Nextcloud
pip3 install requests
vim adduser.py # set user_list
python3 adduser.py
docker exec -it -u 1000 labserver_nextcloud_1 php occ files_external:import my_storages.json
cd ..
```

### enable oauth
* Go to web https://my.domain.ntu.edu.tw:443/oauth/client (If you are admin)
* Add client
``` json
{
"client_id": "qgWmlggGT9Npuihb4ljLyBUd",
"client_secret": "RfxyVQGTY2QUWT6Nj7mgwktXqwilZf3WkQ8DPfi4VUNUIG0r",
"client_name": "testapp",
"client_uri": "https://my.domain.ntu.edu.tw:443/drive/",
"grant_types": ["authorization_code"],
"redirect_uris": ["https://my.domain.ntu.edu.tw:443/drive/apps/sociallogin/custom_oidc/testapp"],
"response_types": ["code"],
"scope": "profile",
"token_endpoint_auth_method": "client_secret_post"
}
```

* Go to web https://my.domain.ntu.edu.tw:443/drive
* Add app `social login`
* Modify code in `Nextcloud//custom_apps/sociallogin/lib/Controller/LoginController.php`
  I have issued this bug https://github.com/zorn-v/nextcloud-social-login/issues/46
* Add client configuration (Custom Oauth2)
``` init
Internal_name: testapp
API_Base_URL:  https://my.domain.ntu.edu.tw:443
Authorize_url: https://my.domain.ntu.edu.tw:443/oauth/authorize
Token_url:     https://my.domain.ntu.edu.tw:443/oauth/token
Profile_url:   https://my.domain.ntu.edu.tw:443/oauth/profile
Clinet_id:
Clinet_Secret:
Scope:         profile
```

You can substitude `testapp` to any you want.


## Contributer
you can use
`git add -p xx`
to add modified things
