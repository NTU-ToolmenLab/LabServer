set -xe
# add traefik and renew key
bash renewcert.sh

echo "Setup Volume"
kubectl create -f k8s/pv.yml -f k8s/pv_user.yml

echo "Install harbor"
helm install --values k8s/harbor.yml --name harbor harbor/harbor-helm

cd k8s/
echo "Add nextcloud"
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml

# Network setting
echo "Add network policy and ingress for traefik"
kubectl create -f policy.yml lab_ingress.yml
cd ..

