#!/bin/bash
set -e

version="v2.12.0"

curl https://storage.googleapis.com/kubernetes-helm/helm-"$version"-linux-amd64.tar.gz --output helm-"$version"-linux-amd64.tar.gz
tar -zxvf helm-"$version"-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm 

rm helm-"$version"-linux-amd64.tar.gz 
rm -rf linux-amd64

touch role-based-access-control-config.yaml
cat <<EOF | sudo tee ./role-based-access-control-config.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: tiller
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: tiller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: tiller
    namespace: kube-system
EOF

kubectl create -f role-based-access-control-config.yaml

helm init --service-account tiller
