# create private registy
kubectl create -f pv.yml -f pv_user.yml

# create harbor
cd harbor-helm
git checkout 1.0.0
# first time
helm install --values ../setting.yml --name harbor .
# update
# helm upgrade -f ../setting.yml harbor .
cd ..

# push container
docker login harbor.default.svc.cluster.local
docker push harbor.default.svc.cluster.local/linnil1/nextcloudfpm:13
docker push harbor.default.svc.cluster.local/linnil1/oauthserver
docker push harbor.default.svc.cluster.local/linnil1/docker-vnc
docker push harbor.default.svc.cluster.local/linnil1/myapi_k8s
docker push harbor.default.svc.cluster.local/linnil1/dockerserver
docker push harbor.default.svc.cluster.local/linnil1/collectgpu

# all services
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml
kubectl create -f OauthServer.yml -f box_redis.yml -f myapi_k8s_set.yml -f DockerServer.yml -f my_vnc.yml -f sshpiper.yml -f lab_ingress.yml 
kubectl create -f collect_gpu.yml

# add traefik and renew key
bash renewcert.sh
