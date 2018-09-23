domain_name='my.domain.ntu.edu.tw'
domain_port=443
nextcloud_port=444
nextcloud_user='admin'
nextcloud_user_password='password'
mysql_root_passowrd='mysql_root_password'
mysql_passowrd='mysql_password'

# domain and port
echo "Change domain name and port and sql password"
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" docker-compose.yml
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" Nextcloud/nginx*
sed -i "s/443:443/$domain_port:443/g" docker-compose.yml
sed -i "s/444:443/$nextcloud_port:443/g" docker-compose.yml
sed -i "s/:443/:$domain_port/g" Nextcloud/nginx.conf

# sql
sed -i "s/MYSQL_ROOT_PASSWORD=/MYSQL_ROOT_PASSWORD=$mysql_root_password/g" docker-compose.yml
sed -i "s/MYSQL_PASSWORD=/MYSQL_PASSWORD=$mysql_password/g" docker-compose.yml

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
sudo mv noVNC/build ../
sudo cp build/vnc.html build/index.html
cat token_plugin.py >> websockify/websockify/token_plugins.py
docker build . -t linnil1/docker-vnc
cd ..

## Build nextcloud
echo "Build nextcloud with id 1000:1000"
docker build Nextcloud -t linnil1/nextcloudfpm

## Build example
echo "Add example"
docker build UserDocker -t linnil1/docker-firefox

## Start all
echo "docker-compose up"
docker-compose up -d

## configure nextcloud
echo "NextCloud setup"
sudo chown 1000:1000 Nextcloud/nextcloud
docker exec -u 1000 -it labserver_nextcloud_1 php occ maintenance:install \
      --database=mysql \
      --database-name=nextcloud \
      --database-host=nextclouddb \
      --database-pass=$mysql_passowrd \
      --database-user=nextcloud \
      --admin-user=$nextcloud_user \
      --admin-pass=$nextcloud_user_password
docker exec -u 1000 -it labserver_nextcloud_1 php occ config:system:set trusted_domains 0  --value=$domain_name:$domain_port
docker exec -u 1000 -it labserver_nextcloud_1 php occ config:system:set trusted_domains 1  --value=$domain_name:$nextcloud_port
docker exec -u 1000 -it labserver_nextcloud_1 php occ config:system:set overwritewebroot   --value=drive
docker exec -u 1000 -it labserver_nextcloud_1 php occ config:system:set lost_password_link --value=disabled
docker exec -u 1000 -it labserver_nextcloud_1 php occ app:install richdocuments
docker exec -u 1000 -it labserver_nextcloud_1 php occ app:install sociallogin
docker exec -u 1000 -it labserver_nextcloud_1 php occ app:enable files_external
sudo sed -i  "s/\$provider\.'-'\.//g" ./Nextcloud/nextcloud/custom_apps/sociallogin/lib/Controller/LoginController.php
docker exec -u 1000 -it labserver_nextcloud_1 php occ config:app:set richdocuments wopi_url --value=https://$domain_name:$nextcloud_port
