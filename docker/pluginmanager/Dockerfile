FROM python:3.7.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install pyyaml
RUN pip install zipfile2

# Bundle app source
COPY pluginmanager.py /

CMD ["python","pluginmanager.py"]
