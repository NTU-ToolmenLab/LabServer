FROM python:3.6-slim
RUN mkdir /app/sock/ -p
COPY . /app/DockerServer/
RUN pip3 install -e /app/DockerServer && \
    pip3 install gunicorn


WORKDIR /app
# command: "gunicorn -b unix:/tmp/DockerServer.sock DockerServer:app --reload"
CMD ["gunicorn", "DockerServer:app", "-b", "unix:/var/run/DockerServer.sock"]
