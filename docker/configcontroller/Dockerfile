FROM python:3.7.0-alpine

# Create stdconfig directory
WORKDIR /

RUN pip install requests
RUN pip install redis
RUN pip install pyyaml

COPY src /dtconfig
COPY configcontroller/configcontroller.py /

CMD ["python","configcontroller.py"]
