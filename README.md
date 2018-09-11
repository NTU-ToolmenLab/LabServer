# LabServer
Some application or dockerfiles run on server

## How to Build
### PreRequire
* docker
* docker-compose
* nvidia-docker

### Clone from GITHUB
```
git clone https://github.com/linnil1/LabServer
cd LabServer
```

### Create encrypt file
1. Use Lets Encrypt it!
**You should open port 80 for verification**

```
docker pull certbot/certbot
docker run --rm -it -p 80:80 -v $PWD/letsencrypt:/etc/letsencrypt certbot/certbot certonly --standalone
```

1.1. Renew it 

`docker run --rm -it -p 80:80 -p 443:443 -v $PWD/letsencrypt:/etc/letsencrypt certbot/certbot renew`

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

## Some variable
`vim run.sh` to edit top few lines.

## OauthServer
### change Nmae of Oauthserver
`vim OauthServer/app.py`

and change `Lab304` to what you want.

## docker_compose network
If you are familiar with Dockernetworking,
you can change your networking in `docker-compose.yml`.

## Run script
`sudo bash run.sh`

## OauthServer
Add User and Container

1. Add it by command line
`docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask std_add_user`
`docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask std_add_box`

For example:
`docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask std_add_box`

and fill 
```
user = linnil1
box = labserver_test_1
docker = labserver_test_1
```

2. Add with code
Modify `std_add_user` in `app.py`, it is very easy.

3. Add it by web (After init)
If you are admin, go to `your.domain.name/adminpage` to modify.

4. You can add `help.html` in `oauthserver/templates/`


## Finally, you can start your server
`docker-compose up -d`

## VNC
If you want to do more fancy things, like auto login for vnc password.
you can add `my_vnc/app/ui.js` with
```
var xmlHttp = new XMLHttpRequest();
xmlHttp.onreadystatechange = function() {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
        password = xmlHttp.responseText;
        // do somethings
    }
}
var tokenname = window.location.search;
tokenname = tokenname.substr(17);
xmlHttp.open("POST", "https://my.domain.ntu.edu.tw:443/box/vnctoken?token=" + tokenname, true); // true for asynchronous 
xmlHttp.send(null);
```

## NextCloud

### init
(Already done in `run.sh`)

I provide two way to login NextCloud.

One is from
`my.domain.ntu.edu.tw:443/drive`

the other is (because collabora not work in reverse proxy)
`my.domain.ntu.edu.tw:444`

and enable `collabora`, `social login`, `external storage` for you.

I issued social login [bug](https://github.com/zorn-v/nextcloud-social-login/issues/46).

### enable external storage
Add External Storage by python
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

* Go to web https://my.domain.ntu.edu.tw:443/drive/settings/admin/sociallogin
* Modify code in `Nextcloud//custom_apps/sociallogin/lib/Controller/LoginController.php`
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
