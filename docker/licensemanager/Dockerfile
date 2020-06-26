FROM python:3.8.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install pyyaml

COPY src /dtconfig

# Bundle app source
#COPY dtconfig /dtconfig
COPY licensemanager/licensequota.yml /
COPY licensemanager/licensemanager.py /

CMD ["python","licensemanager.py"]
