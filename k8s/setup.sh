echo "Setup"
LABSERVER_IP=192.168.1.3
LABSERVER_PATH=/volume1
LABNAS_IP=192.168.1.3
HOMENAS_IP=192.168.1.4
LABNAS_PATH=/volume1
HOMENAS_PATH=/volume1
MASTERIP=$(ip a | grep MASTER -A 5 | grep 'inet ' | awk '{print $2}' | cut -f 1 -d '/')
mysql_root_password='mysql_root_password'
mysql_password='mysql_password'
domain_name='my.domain.ntu.edu.tw'
domain_port=443
oauth_secretkey='secretkey'
oauth_registry_password='registry_password'

sed -i "s~{{\s*LABSERVER_IP\s*}}~$LABSERVER_IP~g" pv.yml
sed -i "s~{{\s*LABSERVER_PATH\s*}}~$LABSERVER_PATH~g" pv.yml
sed -i "s~{{\s*LABNAS_IP\s*}}~$LABNAS_IP~g" pv_user.yml
sed -i "s~{{\s*LABNAS_PATH\s*}}~$LABNAS_PATH~g" pv_user.yml
sed -i "s~{{\s*HOMENAS_IP\s*}}~$HOMENAS_IP~g" pv_user.yml
sed -i "s~{{\s*HOMENAS_PATH\s*}}~$HOMENAS_PATH~g" pv_user.yml
sed -i "s~{{\s*ip\s*}}~$MASTERIP~g" traefik.yml
sed -i "s/{{\s*mysql_root_password\s*}}/$mysql_root_password/g" nextcloud_db.yml
sed -i "s/{{\s*mysql_password\s*}}/$mysql_password/g" nextcloud_db.yml
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" ../Nextcloud/nginx-k8s.conf nextcloud_collabora.yml
sed -i "s/:443/:$domain_port/g" ../Nextcloud/nginx*
sed -i "s/{{\s*secretkey\s*}}/$oauth_secretkey/g" ../OauthServer/config.py
sed -i "s/{{\s*registry_password\s*}}/$oauth_registry_password/g" ../OauthServer/config.py

# build for k8s docker api server
echo "build container"
docker build myapi_k8s -t harbor.default.svc.cluster.local/linnil1/myapi_k8s
docker tag linnil1/nextcloudfpm:13 harbor.default.svc.cluster.local/linnil1/nextcloudfpm:13
docker tag linnil1/oauthserver harbor.default.svc.cluster.local/linnil1/oauthserver
docker tag linnil1/docker-vnc harbor.default.svc.cluster.local/linnil1/docker-vnc
docker tag linnil1/myapi_k8s harbor.default.svc.cluster.local/linnil1/myapi_k8s
docker tag linnil1/dockerserver harbor.default.svc.cluster.local/linnil1/dockerserver
docker tag linnil1/collectgpu harbor.default.svc.cluster.local/linnil1/collectgpu

# build for k8s docker api server
echo "Generate cert for harbor"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=harbor.default.svc.cluster.local" -keyout tls.key -out tls.crt
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local/
sudo cp tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt
kubectl create secret generic harbor-tls --from-file=tls.key --from-file=tls.crt
git clone https://github.com/goharbor/harbor-helm
