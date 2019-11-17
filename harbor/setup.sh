openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=harbor.default.svc.cluster.local" -keyout tls.key -out tls.crt
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local/
sudo cp tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt
cp tls.crt ca.crt
kubectl create secret generic harbor-tls --from-file=tls.key --from-file=tls.crt  --from-file=ca.crt

git clone https://github.com/goharbor/harbor-helm
cd harbor-helm
git checkout 1.1.0


# first time
helm install --values ../setting.yml --name harbor .
# helm upgrade harbor -f ../setting.yml  .
# helm del --pugre harbor
