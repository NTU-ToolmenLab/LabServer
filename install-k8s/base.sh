echo "installing prerequisites"
sudo apt update && \
	sudo apt -y install \
	apt-transport-https \
	ca-certificates \
	curl \
	software-properties-common \
    build-essential

echo "add gpg docker key and stable repository"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

echo "add nvidia-docker2 key"
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

echo "add kubernetes key and repo"
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list

echo "disable swap"
sudo swapoff -a
sudo sed -i 's/^.*swap/#&/' /etc/fstab 

echo "install docker-ce kubectl kubelet kubeadm nvidia-docker2"
sudo apt update && \
sudo apt install -y docker-ce=5:19.03.8~3-0~ubuntu-bionic kubectl=1.18.3-00 kubelet=1.18.3-00 kubeadm=1.18.3-00  kubernetes-cni nvidia-container-toolkit=1.1.1.1

echo "Hold the version"
sudo apt-mark hold docker-ce kubectl kubelet kubeadm kubernetes-cni nvidia-container-toolkit

echo  "Add harbor certification"
sudo mkdir -p /etc/docker/certs.d/harbor.default.svc.cluster.local/
sudo mv ~/tls.crt /etc/docker/certs.d/harbor.default.svc.cluster.local/ca.crt

echo "Add docker config"
sudo groupadd docker
sudo usermod -aG docker $USER
sudo mv ~/daemon.json /etc/docker/daemon.json
sudo systemctl restart docker

# Set parameters and Reload the Docker daemon configuration
# sudo pkill -SIGHUP dockerd

echo "KUBELET_EXTRA_ARGS=--eviction-hard=memory.available<4Gi,nodefs.available<1%,nodefs.inodesFree<1%,imagefs.available<1%,imagefs.inodesFree<1% \
                         --kube-reserved=memory=1Gi \
                         --system-reserved=memory=1Gi \
                         --kube-reserved-cgroup=systemd \
                         --system-reserved-cgroup=systemd" | sudo tee /etc/default/kubelet
sudo systemctl restart kubelet

echo "Set ufw firewall"
if (command -v ufw) && !(sudo ufw status | grep -q inactive); then
    # kube services
    sudo ufw allow 30000:32676/tcp
    # API
    sudo ufw allow 10250/tcp
    # calico
    sudo ufw allow 179,5473/tcp
    sudo ufw allow 4789/udp
fi

echo "Warning!! To below manually"
cat k8s_warning.txt

# echo "nameserver 192.168.23.1" > /etc/resolv_k8s.conf
# echo "Set hostDNS by kubeDNS"
# sudo ln -fs /run/systemd/resolve/resolv.conf /etc/resolv.conf
# echo "nameserver 10.96.0.10" | sudo tee --append  /etc/resolv.conf
