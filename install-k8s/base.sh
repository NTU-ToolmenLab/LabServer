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
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
      sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
      sudo tee /etc/apt/sources.list.d/nvidia-docker.list

echo "add gpg kubernetes key"
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

echo "add k8s repository"
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list

echo "disable swap"
sudo swapoff -a

echo "install docker-ce kubectl kubelet kubeadm nvidia-docker2"
sudo apt update && \
sudo apt install -y docker-ce=5:18.09.6~3-0~ubuntu-bionic nvidia-docker2=2.0.3+docker18.09.6-3 nvidia-container-runtime=2.0.0+docker18.09.6-3\
                    kubectl=1.15.0-00 kubelet=1.15.0-00 kubeadm=1.15.0-00 kubernetes-cni \

echo "Hold the version"
sudo apt-mark hold docker-ce kubectl kubelet kubeadm kubernetes-cni nvidia-docker2 nvidia-container-runtime

echo "Add docker config"
sudo groupadd docker
sudo usermod -aG docker $USER
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl restart docker

# Set parameters and Reload the Docker daemon configuration
# sudo pkill -SIGHUP dockerd

echo "Set ufw firewall"
if ! sudo ufw status | grep -q inactive; then
    # kube services
    sudo ufw allow 30000:32676/tcp
    # API
    sudo ufw allow 10250/tcp
    # calico
    sudo ufw allow 179,5473/tcp
    sudo ufw allow 4789/udp

echo "Set hostDNS by kubeDNS"
sudo ln -fs /run/systemd/resolve/resolv.conf /etc/resolv.conf
echo "nameserver 10.96.0.10" | sudo tee --append  /etc/resolv.conf
