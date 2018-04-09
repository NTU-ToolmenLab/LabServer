FROM python:2.7-slim
RUN apt update -y && apt install build-essential -y
RUN apt install -y xmlsec1
RUN pip install mako cherrypy pycryptodome pycryptodomex passlib
COPY pysaml2 /app/IDP/pysaml2
RUN touch /app/database.db
RUN cd /app/IDP/pysaml2/ && pip install -e .
EXPOSE 8088

WORKDIR /app/IDP/
CMD ["python", "idp.py"]
