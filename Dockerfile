FROM python:3.7
LABEL MAINTAINER=Samiul

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN apt-get update && apt-get install -y tzdata

# create
RUN mkdir /app
WORKDIR /app
# copy requirements.txt to before copying the whole project
# it will save time to install the requirements only once
COPY requirements.txt /app/

# install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy the whole project
COPY . /app/


