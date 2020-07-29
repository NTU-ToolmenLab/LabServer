set -xe

echo "BUILD Nextcloud"
mkdir -p Nextcloud/nextcloud
docker build Nextcloud/ -t linnil1/nextcloudfpm:19
docker tag linnil1/nextcloudfpm:19 harbor.default.svc.cluster.local/linnil1/nextcloudfpm:19

echo "Replace the configuration"
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli Nextcloud/nginx-k8s.conf config.yaml -o Nextcloud/nginx-k8s.conf
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/nextcloud_collabora.yml config.yaml -o k8s/nextcloud_collabora.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/nextcloud_db.yml config.yaml -o k8s/nextcloud_db.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/pv.yml config.yaml -o k8s/pv.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/pv_user.yml config.yaml -o k8s/pv_user.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/traefik.yml config.yaml -o k8s/traefik.yml

echo "Setup Harbor"
cd harbor/certs
cp tls.crt ca.crt
kubectl create secret generic harbor-tls --from-file=tls.key --from-file=tls.crt  --from-file=ca.crt
cd ..
git clone https://github.com/goharbor/harbor-helm
cd harbor-helm
git checkout 1.2.0
cd ../..
