docker run --rm -it -v "$PWD:/app" dcagatay/j2cli Nextcloud/nginx-k8s.conf config.yaml -o Nextcloud/nginx-k8s.conf
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/nextcloud_collabora.yml config.yaml -o k8s/nextcloud_collabora.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/nextcloud_db.yml config.yaml -o k8s/nextcloud_db.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/pv.yml config.yaml -o k8s/pv.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/pv_user.yml config.yaml -o k8s/pv_user.yml
docker run --rm -it -v "$PWD:/app" dcagatay/j2cli k8s/traefik.yml config.yaml -o k8s/traefik.yml
