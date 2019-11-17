# create private registy
kubectl create -f pv.yml -f pv_user.yml

# create harbor
cd harbor-helm
git checkout 1.1.0
# first time
helm install --values ../setting.yml --name harbor .
# update
# helm upgrade -f ../setting.yml harbor .
cd ..

# push container
docker login harbor.default.svc.cluster.local
docker push harbor.default.svc.cluster.local/linnil1/nextcloudfpm:13
docker push harbor.default.svc.cluster.local/linnil1/labboxmain
docker push harbor.default.svc.cluster.local/linnil1/novnc
docker push harbor.default.svc.cluster.local/linnil1/labboxapi-k8s
docker push harbor.default.svc.cluster.local/linnil1/labboxapi-docker
docker push harbor.default.svc.cluster.local/linnil1/collectgpu

# all services
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml
kubectl create -f labboxmain.yml -f labboxdb_redis.yml -f labboxapi_k8s.yml -f labboxapi_docker.yml -f novnc.yml -f sshpiper.yml -f lab_ingress.yml
kubectl create -f collect_gpu.yml
kubectl create -f policy.yml

# add traefik and renew key
bash renewcert.sh
