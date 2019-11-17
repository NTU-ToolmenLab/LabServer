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
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" ../Nextcloud/nginx-k8s.conf nextcloud_collabora.yml ../labboxmain/config.py
sed -i "s/:443/:$domain_port/g" ../Nextcloud/nginx-k8s.conf
sed -i "s/{{\s*secretkey\s*}}/$oauth_secretkey/g" ../labboxmain/config.py
sed -i "s/{{\s*registry_password\s*}}/$oauth_registry_password/g" ../labboxmain/config.py

# Create PV
kubectl create -f pv.yml -f pv_user.yml

# Build images
echo "Build Images"
docker build labboxapi-k8s -t harbor.default.svc.cluster.local/linnil1/labboxapi-k8s
docker tag linnil1/labboxapi-k8s harbor.default.svc.cluster.local/linnil1/labboxapi-k8s
docker tag linnil1/labboxapi-docker harbor.default.svc.cluster.local/linnil1/labboxapi-docker
docker tag linnil1/nextcloudfpm:16 harbor.default.svc.cluster.local/linnil1/nextcloudfpm:16
docker tag linnil1/labboxmain harbor.default.svc.cluster.local/linnil1/labboxmain
docker tag linnil1/novnc harbor.default.svc.cluster.local/linnil1/novnc
docker tag linnil1/collectgpu harbor.default.svc.cluster.local/linnil1/collectgpu

# Build Harbor
echo "Generate cert for harbor"
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=harbor.default.svc.cluster.local" -keyout tls.key -out tls.crt
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local/
sudo cp tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt
kubectl create secret generic harbor-tls --from-file=tls.key --from-file=tls.crt
cd ../harbor
git clone https://github.com/goharbor/harbor-helm
cd harbor-helm
git checkout 1.2.0
helm install harbor -f ../setting.yml .
cd ../../k8s
