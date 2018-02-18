# run traefik
sudo ~/traefik/traefik --api --rest -d
# run vnc
# ...
# update config
curl "http://localhost:8080/api/providers/rest" --upload-file myconfig
# run flask
FLASK_APP=start.py FLASK_DEBUG=1 python3 -m flask run
