FROM python:3.8-buster

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install dnspython
RUN pip install IPy
RUN pip install fqdn
RUN pip install tldextract
RUN pip install pyyaml

# Dynatrace OneAgent SDK
#python -m pip install --upgrade oneagent-sdk

COPY src /dtconfig
COPY config /config
RUN mkdir /config_dump
COPY configmanager/configmanager.py /

CMD ["python","configmanager.py"]
