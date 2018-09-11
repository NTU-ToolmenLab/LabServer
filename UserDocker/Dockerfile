# modify from https://github.com/creack/docker-firefox/blob/master/Dockerfile
From nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
RUN apt update && \
    apt install -y x11vnc xvfb firefox
RUN mkdir ~/.vnc
# Setup a password
RUN x11vnc -storepasswd password ~/.vnc/passwd
# Autostart firefox (might not be the best way to do it, but it does the trick)
RUN bash -c 'echo "firefox" >> ~/.bashrc'
EXPOSE 5900
CMD ["x11vnc", "-forever", "-usepw", "-create"]
