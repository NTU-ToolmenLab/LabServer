#!/bin/bash
set -e

nodes=( "server1" )
node_num=${#nodes[*]}

token=$(sudo kubeadm token create)
token_ca_cert_hash=$(openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //')
master_ip=$(ip addr | grep 'MASTER' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')

echo "creating worker installation script"
cat base.sh > k8s-install-worker-tmp.sh
cat << EOF >> k8s-install-worker-tmp.sh
sudo kubeadm join $master_ip:6443 --token $token --discovery-token-ca-cert-hash sha256:$token_ca_cert_hash
EOF

for (( i=0; i<node_num; i++))
do
    mkdir -p kube_log
	echo "Node: ${nodes[$i]} is joining cluser..."
    # need to set remote server do not need password to execute sudo
    logfile=kube_log/"${nodes[$i]}_$(date +'%Y-%m-%d_%H-%M-%S').log"
    scp daemon.json ${nodes[$i]}:~/ >> $logfile
	scp k8s-install-worker-tmp.sh ${nodes[$i]}:~/ >> $logfile
    # bug: no sync when installing
	ssh -t ${nodes[$i]} "bash k8s-install-worker-tmp.sh" | tee --append $logfile 2>&1
done

times=1
while [ $times -le 21 ]
do
	for (( i=0; i<node_num; i++))
	do
		if [ "$(kubectl get nodes -o wide  | grep ${nodes[$i]} | awk '{print $2}')" == "Ready" ]; then
			echo "node ${nodes[$i]} Ready"
			del=${nodes[$i]}
			nodes=${nodes[@]/$del}
		else
			echo "waiting node ${nodes[$i]}"
		fi
	done
	times=$(( $times+1 ))
	if [ ${#node[*]} -eq 0 ]; then
		break
	fi
	sleep 5
done

echo "Done"

# rm -f k8s-install-worker-tmp.sh
