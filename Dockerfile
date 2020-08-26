FROM python:3.8-alpine
MAINTAINER Ahmed Emad.
ENV PYTHONUNBUFFERED 1
RUN mkdir /InfinityNews
WORKDIR /InfinityNews
COPY . /InfinityNews
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN apk add --update --no-cache postgresql-client postgresql jpeg-dev zlib-dev libjpeg
RUN pip3 install -r /InfinityNews/requirements.txt
RUN apk del .tmp-build-deps
RUN adduser -D InfinityNews
USER InfinityNews
RUN echo "5 * * * * python3 manage.py scrape" | crontab -
