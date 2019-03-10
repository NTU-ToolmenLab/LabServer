echo "installing prerequisites"
sudo apt update && \
	sudo apt -y install \
	apt-transport-https \
	ca-certificates \
	curl \
	software-properties-common

echo "add gpg docker key and stable repository"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
	"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
	$(lsb_release -cs) \
	stable"
sudo groupadd docker
sudo usermod -aG docker $USER

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
sudo apt install -y docker-ce=18.06.0~ce~3-0~ubuntu kubectl kubelet kubeadm kubernetes-cni \
                 nvidia-container-runtime=2.0.0+docker18.06.0-1 nvidia-docker2=2.0.3+docker18.06.0-1

# Set parameters and Reload the Docker daemon configuration
# sudo pkill -SIGHUP dockerd

echo "Setting network"
if ! sudo ufw status | grep -q inactive; then
    # kube services
    sudo ufw allow 30000:32676/tcp
    # etcd client
    sudo ufw allow 2379,2380/tcp
    # healthcheck
    sudo ufw allow 10250/tcp
    # calico
    sudo ufw allow 109/tcp

sudo ln -fs /run/systemd/resolve/resolv.conf /etc/resolv.conf
echo "nameserver 10.96.0.10" | sudo tee --append  /etc/resolv.conf

sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl restart docker
