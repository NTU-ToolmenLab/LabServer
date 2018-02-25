# modify from https://github.com/creack/docker-firefox/blob/master/Dockerfile
From ubuntu:16.04
RUN apt update

# Install vnc, xvfb in order to create a 'fake' display and firefox
RUN apt install -y x11vnc xvfb firefox
RUN mkdir ~/.vnc
# Setup a password
RUN x11vnc -storepasswd 1234 ~/.vnc/passwd
# Autostart firefox (might not be the best way to do it, but it does the trick)
RUN bash -c 'echo "firefox" >> ~/.bashrc'
EXPOSE 5900
CMD ["x11vnc", "-forever", "-usepw", "-create"]
