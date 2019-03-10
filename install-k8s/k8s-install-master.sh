#!/bin/bash
set -e

#pod_network="flannel"
pod_network="calico"
master_no_taint="true"

if [ $pod_network = "flannel" ]; then
    pod_network_cidr="10.244.0.0/16"
elif [ $pod_network = "calico" ]; then
    pod_network_cidr="10.90.0.0/16"
else
    echo "There is no pod network cidr"
fi

bash base.sh

echo "initialize the master node"
sudo kubeadm init --pod-network-cidr="$pod_network_cidr" --service-cidr=10.96.0.0/12

echo "let kubeaadm can be used as a regular user"
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo -n "checking kubelet status..."
sudo systemctl status kubelet | grep "active (running)" &> /dev/null
if [ $? == 0 ]; then
	echo "OK"
else
	echo "not ready"
fi

if [ "$master_no_taint" = true ]; then
    kubectl taint nodes --all node-role.kubernetes.io/master-
fi

if [ $pod_network = "flannel" ]; then
    echo "installing Flannel"
    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
elif [ $pod_network = "calico" ]; then
    echo "installing Calico"
    wget https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/kubernetes-datastore/calico-networking/1.7/calico.yaml
    sed -ie "s~192.168.0.0/16~$pod_network_cidr~g" calico.yaml
    kubectl apply -f calico.yaml -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/rbac-kdd.yaml
else
    echo "there is no pod network assigned!"
    exit 1
fi

echo -n "checking master node status..."

if ! sudo ufw status | grep -q inactive; then
    # kube API
    sudo ufw allow 6443/tcp
    # web
    sudo ufw allow 80,443/tcp
    # kube-scheduler controller
    sudo ufw allow 10251,10252/tcp

ready=false
while [ $ready == false ]
do
	if [ $(kubectl get node | grep master | awk '{print $2}') == "Ready" ]; then
		ready=true
		echo "OK"
	else
		echo -n "."
	fi
	sleep 1
done

echo "source <(kubectl completion bash)" >> ~/.bashrc
