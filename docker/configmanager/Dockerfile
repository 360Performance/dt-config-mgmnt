FROM python:3.10-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests redis dnspython IPy fqdn tldextract pyyaml
RUN pip install schema
RUN pip install coverage
#RUN pip install redis && \
#RUN pip install dnspython && \
#RUN pip install IPy
#RUN pip install fqdn
#RUN pip install tldextract
#RUN pip install pyyaml

COPY . /
#COPY config /config
RUN mkdir /config && mkdir /config_dump

CMD ["python","configmanager.py"]
