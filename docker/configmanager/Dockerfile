FROM python:3.10-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install dnspython
RUN pip install IPy
RUN pip install fqdn
RUN pip install tldextract
RUN pip install pyyaml

COPY configmanager /
#COPY config /config
RUN mkdir /config
RUN mkdir /config_dump

CMD ["python","configmanager.py"]
