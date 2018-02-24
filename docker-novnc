FROM ubuntu:16.04
RUN apt update
RUN apt -y install net-tools python python-numpy
RUN mkdir /app/my_vnc -p

WORKDIR /app
# CMD ["python", "my_vnc/utils/launch.sh", "--vnc", "0.0.0.0:5900", "--web", "my_vnc/build", "]
CMD ["python", "my_vnc/utils/websockify/run", ":6080", "--token-plugin", "dbToken", "--token-source", "/app/database.db", "--web", "my_vnc/build/"]
