FROM python:3.7.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install pyyaml

# Bundle app source
#COPY dtconfig /dtconfig
COPY licensequota.yml /
COPY licensemanager.py /

CMD ["python","licensemanager.py"]
