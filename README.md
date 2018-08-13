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
vim app.py # modify secrect_key and my.domain:443 and path 
docker build . -t linnil1/oauthserver
docker run -it --rm -v $(pwd)/db.sqlite:/app/db.sqlite linnil1/oauthserver flask initdb
```

## Add User and Container
1. Add it by command line
`docker run -it --rm -v $(pwd)/db.sqlite:/app/db.sqlite linnil1/oauthserver flask std_add_user`
`docker run -it --rm -v $(pwd)/db.sqlite:/app/db.sqlite linnil1/oauthserver flask std_add_box`

2. Add with code
Modify `std_add_user` in `app.py`, it is very easy.

3. Add it by web (After init)
If you are admin, go to `your.domain.name/adminpage` to modify.

## Control docker to start or stop
```
cd DockerServer
docker build . -t linnil1/dockerserver
cd ..
```

## build example docker-firefox-vnc (for testing)
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

## Build IDP
you can see some difference of my version
https://gist.github.com/linnil1/b782dc567b1f404efcdb71a643ddc7e4

```
cd IDP
git clone https://github.com/IdentityPython/pysaml2.git
vim idp_conf.py # modify my.domain:443
vim idp.py #  modify "redirect_uri": redirect_uri.replace("http","https").replace(":443",":443/saml")
docker build . -t linnil1/idp
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


## build saml
1. modify my.domain:443
2. modify x509cers

```
cd saml
vim settings.json 
cd ../..
```


## Modify docker-compose
1. change host from 127.0.0.1 to my.domain
2. change port from 443 and 8888 if you want
3. nextcloud_db password
4. nextcloud external data path

vim docker-compose.yml

## Finally, you can start your server
`docker-compose up -d`

## NextCloud
### init
Go in to web https://my.domain.ntu.edu.tw:444

Set admin and password, and choose mysql: hostname=nextclouddb, and the other are same as docker-compose written

enable "collabora" (Set https://my.domain.ntu.edu.tw:444)

### SSO

enable "SSO & SAML authentication" and set like this

```
"types": "authentication",
"type": "saml",
"general-idp0_display_name": "LoginName",
"general-allow_multiple_user_back_ends": "1",
"general-uid_mapping": "uid",
"saml-attribute-mapping-displayName_mapping": "uid",
"saml-attribute-mapping-quota_mapping": "quota",
"idp-entityId": "myEntityID",
"idp-singleSignOnService.url": "https:\/\/my.domain.ntu.edu.tw:443\/saml\/sso\/redirect",
"idp-singleLogoutService.url": "https:\/\/my.domain.ntu.edu.tw:443\/saml\/slo\/redirect",
```

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

## Contributer
you can use
`git add -p xx`
to add modified things
