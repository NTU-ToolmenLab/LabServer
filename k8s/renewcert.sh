echo "Change ip and cert and key"
kubectl create secret generic test --from-file=../certs/fullchain.pem --from-file=../certs/privkey.pem
sec_cert=$(kubectl get secrets test -o yaml | grep fullchain | awk {'print $2}')
sec_key=$(kubectl get secrets test -o yaml | grep privkey | awk {'print $2}')
sed -i "s/defaultCert.*/defaultCert: $sec_cert/g" traefik.yml
sed -i "s/defaultKey.*/defaultKey: $sec_key/g" traefik.yml
kubectl delete secrets test

# First time
# helm install lab-traefik stable/traefik -f traefik.yml
# Update
helm upgrade lab-traefik -f traefik.yml stable/traefik 
kubectl rollout restart deployment lab-traefik
