FROM python:3.6-slim
RUN pip3 install numpy
RUN mkdir /app
RUN touch /app/database.db

WORKDIR /app
EXPOSE 6080
# python3 my_vnc/websockify/websockify.py :6080 --token-plugin dbToken --token-source /app/database.db --web my_vnc/build
CMD ["python3", "my_vnc/websockify/websockify.py", ":6080", "--token-plugin", "dbToken", "--token-source", "/app/database.db", "--web", "my_vnc/build"]
