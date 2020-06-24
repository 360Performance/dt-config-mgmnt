FROM python:3.7.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install dnspython
RUN pip install IPy
RUN pip install fqdn
RUN pip install tldextract
RUN pip install pyyaml

COPY src /dtconfig
COPY config /config
RUN mkdir /config_dump
COPY configmanager/configmanager.py /

CMD ["python","configmanager.py"]
