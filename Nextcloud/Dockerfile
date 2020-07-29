FROM nextcloud:19-fpm
RUN apt update && apt install sudo -y
RUN usermod -u 1000 www-data && \
    groupmod -g 1000 www-data 
