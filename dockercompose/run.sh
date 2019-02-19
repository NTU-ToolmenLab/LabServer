domain_name='my.domain.ntu.edu.tw'
domain_port=443
nextcloud_port=444
nextcloud_user='admin'
nextcloud_user_password='password'
mysql_root_passowrd='mysql_root_password'
mysql_passowrd='mysql_password'
portus_password='portus_password'

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

# portus certs
sed -i "s/dbpw:/dbpw: $mysql_passowrd/g" k8s/portus_config.yml
sed -i "s/secretkey:/secretkey: $portus_password/g" k8s/portus_config.yml


## Build example
echo "Add example"
docker build UserDocker -t linnil1/docker-firefox

## Start all
echo "docker-compose up"
docker-compose up -d

## configure nextcloud
echo "NextCloud setup"
# k8s
# app=kubectl
# nextcloudapp=$(kubectl get pod -l name=nextcloud-fpm -o name)
# nextclouddb='nextcloud-db.default.svc.cluster.local'
app=docker
nextcloudapp='labserver_nextcloud_1'
nextclouddb='nextcloud-db'
sudo chown 1000:1000 Nextcloud/nextcloud
$app exec -u 1000 -it $nextcloudapp php occ maintenance:install \
      --database=mysql \
      --database-name=nextcloud \
      --database-host=$nextclouddb \
      --database-pass=$mysql_passowrd \
      --database-user=nextcloud \
      --admin-user=$nextcloud_user \
      --admin-pass=$nextcloud_user_password
$app exec -u 1000 -it $nextcloudapp php occ config:system:set trusted_domains 0  --value=$domain_name:$domain_port
$app exec -u 1000 -it $nextcloudapp php occ config:system:set trusted_domains 1  --value=$domain_name:$nextcloud_port
$app exec -u 1000 -it $nextcloudapp php occ config:system:set overwritewebroot   --value=drive
$app exec -u 1000 -it $nextcloudapp php occ config:system:set lost_password_link --value=disabled
$app exec -u 1000 -it $nextcloudapp php occ app:install richdocuments
$app exec -u 1000 -it $nextcloudapp php occ app:install sociallogin
$app exec -u 1000 -it $nextcloudapp php occ app:enable files_external
sudo sed -i  "s/\$provider\.'-'\.//g" ./Nextcloud/nextcloud/custom_apps/sociallogin/lib/Controller/LoginController.php
$app exec -u 1000 -it $nextcloudapp php occ config:app:set richdocuments wopi_url --value=https://$domain_name:$nextcloud_port
