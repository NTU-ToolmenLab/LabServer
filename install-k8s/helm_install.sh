#!/bin/bash
set -e

version="v3.2.1"

wget https://get.helm.sh/helm-"$version"-linux-amd64.tar.gz
tar -zxvf helm-"$version"-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm 

rm helm-"$version"-linux-amd64.tar.gz 
rm -rf linux-amd64

helm repo add stable  https://kubernetes-charts.storage.googleapis.com

