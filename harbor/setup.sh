openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=harbor.default.svc.cluster.local" -keyout tls.key -out tls.crt
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local/
sudo cp tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt
kubectl create secret generic harbor-tls --from-file=tls.key --from-file=tls.crt 

git clone https://github.com/goharbor/harbor-helm
cd harbor-helm
git checkout 1.0.0


# first time
helm install --values traefik.yml --name harbor stable/traefik
# update
# helm upgrade lab-traefik -f traefik.yml stable/traefik
