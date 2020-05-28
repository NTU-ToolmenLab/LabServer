# push container
docker login harbor.default.svc.cluster.local

# all services
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml
kubectl create -f policy.yml lab_ingress.yml
kubectl create -f collect_gpu.yml

# add traefik and renew key
bash renewcert.sh
