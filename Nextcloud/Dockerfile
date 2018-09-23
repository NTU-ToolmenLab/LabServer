FROM nextcloud:fpm

RUN usermod -u 1000 www-data && \
    groupmod -g 1000 www-data

ENTRYPOINT ["/entrypoint.sh"]
CMD ["php-fpm"]
