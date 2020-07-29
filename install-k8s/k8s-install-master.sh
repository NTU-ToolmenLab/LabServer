#!/bin/bash
set -e

#pod_network="flannel"
pod_network="calico"
master_no_taint="true"
interface="bond0"

if [ $pod_network = "flannel" ]; then
    pod_network_cidr="10.244.0.0/16"
elif [ $pod_network = "canal" ]; then
    pod_network_cidr="10.244.0.0/16"
elif [ $pod_network = "calico" ]; then
    pod_network_cidr="10.90.0.0/16"
else
    echo "There is no pod network cidr"
    exit
fi

echo "Create harbor certificaton"
mkdir -p ../harbor/certs
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -subj "/C=TW/CN=harbor.default.svc.cluster.local" -keyout ../harbor/certs/tls.key -out ../harbor/certs/tls.crt
cp ../harbor/certs/tls.crt .

echo "Run basic config"
cp tls.crt ~/
cp daemon.json ~/
bash base.sh

echo "initialize the master node"
sudo kubeadm init --pod-network-cidr="$pod_network_cidr" --service-cidr="10.96.0.0/12"

echo "let kubeaadm can be used as a regular user"
mkdir -p $HOME/.kube
sudo cp -f /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo "checking kubelet status..."
sudo systemctl status kubelet | grep "active (running)" &> /dev/null
if [ $? == 0 ]; then
	echo "OK"
else
	echo "not ready"
fi

echo "Remove master taint"
if [ "$master_no_taint" = true ]; then
    kubectl taint nodes --all node-role.kubernetes.io/master-
fi

if [ $pod_network = "flannel" ]; then
    echo "installing Flannel"
    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
elif [ $pod_network = "calico" ]; then
    echo "installing Calico"
    rm -f calico.yaml
    wget https://docs.projectcalico.org/archive/v3.13/manifests/calico.yaml
    sed -ie "/autodetect/a\
\            - name: IP_AUTODETECTION_METHOD\n\
\              value: interface=$interface" calico.yaml
    kubectl apply -f calico.yaml
elif [ $pod_network = "canal" ]; then
    echo "installing Canal"
    kubectl apply -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/canal/rbac.yaml
    kubectl apply -f https://docs.projectcalico.org/v3.3/getting-started/kubernetes/installation/hosted/canal/canal.yaml
else
    echo "there is no pod network assigned!"
    exit 1
fi

echo "Add kubectl autocompletion"
echo "source <(kubectl completion bash)" >> ~/.bashrc

echo "Set ufw firewall"
if (command -v ufw) && !(sudo ufw status | grep -q inactive); then
    # kube API
    sudo ufw allow 6443/tcp
    # kube etcd
    sudo ufw allow 2379,2380/tcp
    # web
    sudo ufw allow 80,443/tcp
    # kube-scheduler controller
    sudo ufw allow 10251,10252/tcp
fi

echo -n "checking master node status..."

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

echo "Done"
