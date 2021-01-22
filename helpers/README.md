### Use Case: Expose a tcp socket for accessing docker API
This is useful for MacOS to expose the docker API for other hosts to access. e.g. for Jenkins jobs that deploy to other docker hosts

https://hub.docker.com/r/alpine/socat/

$ docker pull alpine/socat
$ docker run -d --restart=always \
    -p 0.0.0.0:2376:2375 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    alpine/socat \
    tcp-listen:2375,fork,reuseaddr unix-connect:/var/run/docker.sock