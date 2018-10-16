domain_name='my.domain.ntu.edu.tw'
mysql_root_passowrd='mysql_root_password'
mysql_passowrd='mysql_password'
LABNAS_IP=192.168.1.3
HOMENAS_IP=192.168.1.4
LABNAS_PATH=\/path
HOMENAS_PATH=\/path
LABSERVER_IP=192.168.1.4
LABSERVER_PATH=\/path

# test
echo "Change ip and cert and key"
vim traefik.yml

docker build myapi_k8s -t registry-svc.default.svc.cluster.local:5002/linnil1/myapi_k8s

# domain and port
echo "Change domain name and port and sql password"
sed -i "s/my.domain.ntu.edu.tw/$domain_name/g" ../Nextcloud/nginx* nextcloud_collabora.yml
sed -i "s/mysql_root_password/$mysql_root_password/g" nextcloud_db.yml
sed -i "s/mysql_passowrd/$mysql_password/g" nextcloud_db.yml

sed -i "s/\$LABNAS_IP/$LABNAS_IP/g" pv_labnas.yml
sed -i "s/\$LABNAS_PATH/$LABNAS_PATH/g" pv_labnas.yml
sed -i "s/\$HOMENAS_IP/$HOMENAS_IP/g" pv_homenas.yml
sed -i "s/\$HOMENAS_PATH/$HOMENAS_PATH/g" pv_homenas.yml
sed -i "s/\$LABSERVER_IP/$LABSERVER_IP/g" pv.yml
sed -i "s/\$LABSERVER_PATH/$LABSERVER_PATH/g" pv.yml


helm install stable/traefik --name lab-traefik --values traefik.yml
