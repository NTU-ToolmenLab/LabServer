# LabServer with k8s

This repo integrate all the serivce related to toolmen.

Service that integrated:
* Installation of all
* Nextcloud(like google drive)
* traefik(load balancer)
* network policy(`k8s/policy.yml`: cannot access internal ip from user's instance)
* Certification
* harbor(docker registry)
* [labbox](https://github.com/NTU-ToolmenLab/labbox): The main service for Toolmen lab.

## Related repo
[Dockerfile](https://github.com/NTU-ToolmenLab/LabDockerFile)
[Monitor](https://github.com/NTU-ToolmenLab/LabServer_monitor)
[labbox](https://github.com/NTU-ToolmenLab/labbox)


### Use with dockercompsoe
**It has not been maintained now.**

## How to Use with k8s

### 0. Make sure
* ssh
* git
* nvidia-driver
* You have nameserver: [10.96.0.10, 8.8.8.8] in local(Use netplan)

### 1. Clone from Github
```
git clone https://github.com/linnil1/LabServer
cd LabServer
```

### 2. Install k8s and build k8s cluster
Install k8s for master machine
```
cd install-k8s/
./k8s-install-master.sh
./helm_install.sh
cd ..
```

Install k8s for worker machine.

(Note: Worker servers can be logined via sshkey from master)

```
cd install-k8s/
./k8s-install-slave.sh server1 server2
cd ..
```

### 3. Setting and Init Setup
Set your own secret data, e.g. ip, path, nas configuration

Rename and change the setting in `config.example.yaml` to `config.yaml`

`./setup.sh` will

* Replace the variable 
* Build image from dockerfile for nextcloud
* Setup harbor setting

### 4. Set Certification
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

Finally, restart the pods with new certification
`./renewcert.sh`


### 5. Start
`./start_service.sh`

### 6. Setup harbor
#### Login
* Default User: admin
* Default Password: Harbor12345

#### Add regstries
* Provider: docker-registry
* Endpoint: http://harbor-harbor-registry.default.svc.cluster.local:5000
* SSL: no

#### Test
```
docker login harbor.default.svc.cluster.local
docker push harbor.default.svc.cluster.local/linnil1/nextcloudfpm:19
```

## Finally, Install labbox(Main interface)
```
git clone https://github.com/NTU-ToolmenLab/labbox.git
cd labbox
```
and follow the guide in https://github.com/NTU-ToolmenLab/labbox



## Some note

### Network Policy
https://hackmd.io/dZEPlsD0S22ZKBPe53iFXg

### Nextcloud Enable Oauth
Go to oauth setting web https://my.domain.ntu.edu.tw:443/oauth/client (If you are admin)

Add client
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

Modify code in Nextcloud/nextcloud/custom_apps/sociallogin/lib/Service/ProviderService.php to make login with their name `$uid = $profileId;`

Go to setting web https://my.domain.ntu.edu.tw:443/drive/settings/admin/sociallogin

Add client configuration (Custom Oauth2)
``` init
Internal_name: testapp
API_Base_URL:  https://my.domain.ntu.edu.tw:443
Authorize_url: https://my.domain.ntu.edu.tw:443/oauth/authorize
Token_url:     https://my.domain.ntu.edu.tw:443/oauth/token
Profile_url:   https://my.domain.ntu.edu.tw:443/oauth/profile
Clinet_id:
Clinet_Secret:
Scope:         profile
Groups claim (optional): groups
Group mapping: fill it
```

You can substitude `testapp` to any you want(Should be consistent between oauth client and server).
