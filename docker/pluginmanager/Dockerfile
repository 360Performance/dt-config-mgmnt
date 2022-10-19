FROM python:3.8.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install pyyaml
RUN pip install zipfile2

COPY src /dtconfig
COPY pluginmanager.py /

CMD ["python","pluginmanager.py"]
