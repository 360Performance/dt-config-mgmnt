FROM redis

RUN apt-get update
RUN apt-get install -y expect

COPY redis.listen /usr/bin/redis.listen
RUN chmod 755 /usr/bin/redis.listen

COPY redis.conf /usr/local/etc/redis/redis.conf
CMD [ "/usr/local/etc/redis/redis.conf" ]