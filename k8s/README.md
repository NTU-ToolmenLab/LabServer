# LabServer k8s configuratrion

## Setup

Modify `setup.sh`.

and run `bash setup.sh`


### Add new nodes
If you add new nodes, you should remember to copy certs of Harbor to `/etc/docker`.

```
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local
sudo cp ./harbor/tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt
```

## Run

`bash run.sh`

## Renew Certification

`bash renewcert.sh`
