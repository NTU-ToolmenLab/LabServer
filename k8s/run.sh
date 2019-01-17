# create private registy
kubectl create -f pv.yml -f pv_user.yml
kubectl create -f portus.yml -f portus_config.yml -f portus_db.yml -f portus_registry.yml 

# push container
docker login registy.default.svc.cluster.local
docker push registry.default.svc.cluster.local/linnil1/nextcloudfpm:13
docker push registry.default.svc.cluster.local/linnil1/oauthserver
docker push registry.default.svc.cluster.local/linnil1/docker-vnc
docker push registry.default.svc.cluster.local/linnil1/myapi_k8s
docker push registry.default.svc.cluster.local/linnil1/dockerserver

# all services
kubectl create -f nextcloud_fpm.yml -f nextcloud_web.yml -f nextcloud_collabora.yml -f nextcloud_db.yml
kubectl create -f OauthServer.yml -f box_redis.yml -f myapi_k8s_set.yml -f DockerServer.yml -f my_vnc.yml -f sshpiper.yml -f lab_ingress.yml 

# add traefik and renew key
bash renewcert.sh
