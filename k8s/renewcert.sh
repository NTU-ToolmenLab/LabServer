echo "Change ip and cert and key"
kubectl create secret generic test --from-file=../certs/fullchain.pem --from-file=../certs/privkey.pem
sec_cert=$(kubectl get secrets test -o yaml | grep fullchain | awk {'print $2}')
sec_key=$(kubectl get secrets test -o yaml | grep privkey | awk {'print $2}')
sed -i "s/defaultCert.*/defaultCert: $sec_cert/g" traefik.yml
sed -i "s/defaultKey.*/defaultKey: $sec_key/g" traefik.yml
kubectl delete secrets test

helm del --purge lab-traefik
helm install stable/traefik --name lab-traefik --values traefik.yml
