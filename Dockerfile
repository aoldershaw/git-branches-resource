ARG base_image=alpine:latest

FROM ${base_image} AS resource

RUN apk add --no-cache \
  bash \
  git \
  jq

WORKDIR /root
RUN apk add --no-cache \
    --virtual build-dependencies \
    make \
    g++ \
    openssl-dev && \
  git clone https://github.com/proxytunnel/proxytunnel.git && \
  cd proxytunnel && \
  make -j4 && \
  install -c proxytunnel /usr/bin/proxytunnel && \
  cd .. && \
  rm -rf proxytunnel && \
  apk del build-dependencies

RUN git config --global user.email "git@localhost"
RUN git config --global user.name "git"

ADD assets/ /opt/resource/
RUN chmod +x /opt/resource/*
