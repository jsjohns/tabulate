FROM openjdk:7

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip \
    imagemagick \
    tesseract-ocr \
    libmagic-dev

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ADD bin/tabula-0.9.1-jar-with-dependencies.jar /bin/

ENTRYPOINT /data/app.py