# LabServer With K8S

The advantage of this labserver is that user can access GPU resources
with prebuild docker images(which contain pytorch, keras and caffe2),
they can also choose which server to start their containers.

After starting containers, they access it by ssh(sshpiper) or vnc(noVNC) we provided,
the vnc is a graphical user interface that can run in any browser without install anything.

With the help of Docker and Kubernetes, this system should be safe, secure and reliable.

Moreover, this repo provide more applications like Nextcloud(Drive), Grafana(Monitor)
to make life easier.

## Related repo
[Dockerfile](https://github.com/armorsun/Lab304-server)
[Monitor](https://github.com/linnil1/LabServer_monitork)

## How to Build

### Clone from Github 
```
git clone https://github.com/linnil1/LabServer
cd LabServer
```

### Create encrypt file
1. Use Lets Encrypt it!
**You should open port 80 and 443 for verification**

```
docker pull certbot/certbot
docker run --rm -it -p 80:80 -v $PWD/letsencrypt:/etc/letsencrypt certbot/certbot certonly --standalone
```

1.1. Renew it 

`docker run --rm -it -p 80:80 -p 443:443 -v $PWD/letsencrypt:/etc/letsencrypt certbot/certbot renew`

Then copy to `certs/`

`cp letsencrypt/live/my.domain.ntu.edu.tw/* certs/`

2. Self-signed
```
cd certs
openssl genrsa 1024 > privkey.pem
chmod 400 privkey.pem
openssl req -new -x509 -nodes -sha1 -days 365 -key privkey.pem -out fullchain.pem
cd ..
```

### build dockerfile
`bash setup.sh`

### build with k8s
You can initize your new server with this note
https://hackmd.io/V40UgNo3S4mp4cUtT3yY-g#

Then install
* docker
* nvidia-docker
* kubernetes
```
cd install
./k8s-install-master.sh
```

Add more servers as slave.

Change the `nodes` in `k8s-install-worker.sh`,
and you should make sure that `ssh server` can work without entering password.
```
./k8s-install-worker.sh
```

The next step: setup all services and deployments.

see `k8s/README.md`

### build with dockercompsoe

see `README-dockercompose.md`.

**It has been not maintained now.**


## Some note of this system

### OauthServer
This app has two features:
1. Oauth Server
2. A interface that can start or stop your containers.

1.  Run this code to add more users.
```
docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask std-add-user
```
2. Add it by web (After init)
If you are admin, go to `your.domain.name/adminpage` to modify.


You can add `help.html` in `Oauthserver/oauthserver/templates/`

### VNC
If you want to do more fancy things, like auto login for vnc password.
you can add `my_vnc/noVNC/app/ui.js` with
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

### Nextcloud Enable Oauth
* Go to web https://my.domain.ntu.edu.tw:443/oauth/client (If you are admin)
* Add client
``` json
{
"client_id": "",
"client_secret": "",
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


### Nextcloud set external storage by Python
``` shell
cd Nextcloud
pip3 install requests
vim adduser.py
python3 adduser.py
docker exec -it -u 1000 labserver_nextcloud_1 php occ files_external:import my_storages.json
cd ..
```

## Contribute
you can use `git add -p xx` to commit modified changes.
