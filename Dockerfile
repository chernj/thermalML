FROM alpine:edge

MAINTAINER <support@collectiveacuity.com>

# Update Alpine environment
RUN echo '@edge http://nl.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories
RUN echo '@community http://nl.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories
RUN echo '@testing http://nl.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
RUN apk update
RUN apk upgrade
RUN apk add ca-certificates

# Install Python & Pip
RUN apk add curl
RUN apk add python
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

# Install C Compiler Dependencies
RUN apk add gcc
RUN apk add g++

# Install Python Modules
RUN pip install python-telegram-bot

# Install Localtunnel
# RUN apk add nodejs@community
# RUN npm install -g npm
# RUN npm install -g localtunnel

# Clean APK cache
RUN rm -rf /var/cache/apk/*
