echo "Change ip and cert and key"
kubectl create secret generic test --from-file=certs/fullchain.pem --from-file=certs/privkey.pem
sec_cert=$(kubectl get secrets test -o jsonpath="{.data.fullchain\.pem}")
sec_key=$(kubectl get secrets test -o jsonpath="{.data.privkey\.pem}")
sed -i "s/defaultCert.*/defaultCert: $sec_cert/g" k8s/traefik.yml
sed -i "s/defaultKey.*/defaultKey: $sec_key/g" k8s/traefik.yml
kubectl delete secrets test

# helm install
if (helm list | grep lab-traefik); then
    helm upgrade lab-traefik -f k8s/traefik.yml stable/traefik 
    kubectl rollout restart deployment lab-traefik
else
    helm install lab-traefik stable/traefik -f k8s/traefik.yml
fi
