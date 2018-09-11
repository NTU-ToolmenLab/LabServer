FROM python:3.7-slim
RUN pip3 install numpy
RUN mkdir -p /app/myvnc
RUN touch /app/db.sqlite

WORKDIR /app/my_vnc
EXPOSE 6080
# "python3 websockify/websockify.py :6080 --token-plugin dbToken --token-source /app/db.sqlite --web build"
CMD ["python3", "websockify/websockify.py", ":6080", "--token-plugin", "dbToken", "--token-source", "/app/db.sqlite", "--web", "build"]
