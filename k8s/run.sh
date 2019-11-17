# push container
docker login harbor.default.svc.cluster.local
docker push harbor.default.svc.cluster.local/linnil1/nextcloudfpm:16
docker push harbor.default.svc.cluster.local/linnil1/labboxmain
docker push harbor.default.svc.cluster.local/linnil1/novnc
docker push harbor.default.svc.cluster.local/linnil1/labboxapi-k8s
docker push harbor.default.svc.cluster.local/linnil1/labboxapi-docker
docker push harbor.default.svc.cluster.local/linnil1/collectgpu

# all services
kubectl create -f lab_ingress.yml -f policy.yml
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml
kubectl create -f labboxmain.yml -f labboxdb_redis.yml -f labboxapi_k8s.yml -f labboxapi_docker.yml -f novnc.yml -f sshpiper.yml
kubectl create -f collect_gpu.yml

# add traefik and renew key
bash renewcert.sh
