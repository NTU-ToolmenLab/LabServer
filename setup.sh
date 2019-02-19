# build oauth
echo "BUILD OauthServer"
docker build OauthServer -t linnil1/oauthserver
docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask initdb
docker run -it --rm -v $PWD/OauthServer:/app/OauthServer linnil1/oauthserver flask std_add_user

# Control docker to start or stop
echo "BUILD dockerserver"
docker build DockerServer -t linnil1/dockerserver

## VNC
echo "BUILD VNC"
cd my_vnc
git clone https://github.com/novnc/websockify
git clone https://github.com/novnc/noVNC.git
docker run -it --rm -v $PWD/noVNC:/project node:8.11-alpine sh -c ' \
  cd /project && npm install . && ./utils/use_require.js --with-app --as commonjs'
sudo mv noVNC/build ./
sudo cp build/vnc.html build/index.html
cat token_plugin.py >> websockify/websockify/token_plugins.py
docker build . -t linnil1/docker-vnc
cd ..

## nextcloud
echo "BUILD Nextcloud"
mkdir -p Nextcloud/nextcloud
docker build Nextcloud/ -t linnil1/nextcloudfpm:15

## Portus Certs
echo "Set Portus Cert"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=registry.default.svc.cluster.local" -keyout ./Portus/certs/privkey.pem -out ./Portus/certs/cert.pem
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=portus.default.svc.cluster.local" -keyout ./Portus/certs/portus_privkey.pem -out ./Portus/certs/portus_cert.pem
sudo mkdir -p /etc/docker/certs.d/registry.default.svc.cluster.local
sudo cp ./Portus/certs/cert.pem /etc/docker/certs.d/registry.default.svc.cluster.local/ca.crt
sudo cp ./Portus/certs/portus_cert.pem /etc/docker/certs.d/registry.default.svc.cluster.local/client.crt
