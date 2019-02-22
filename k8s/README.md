# LabServer k8s configuratrion

## Setup

Modify `setup.sh`.

and run `bash setup.sh`


### Add new nodes
If you add new nodes, you should remember to copy certs of Portus to `/etc/docker`.

```
sudo mkdir -p /etc/docker/certs.d/registry.default.svc.cluster.local
sudo cp ./Portus/certs/cert.pem /etc/docker/certs.d/registry.default.svc.cluster.local/ca.crt
sudo cp ./Portus/certs/portus_cert.pem /etc/docker/certs.d/registry.default.svc.cluster.local/client.crt
```

## Run

`bash run.sh`

## Renew Certification

`bash renewcert.sh`
