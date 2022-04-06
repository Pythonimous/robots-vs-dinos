# syntax=docker/dockerfile:1

# python image to use
FROM python:3.8-slim-buster

# use same directory and name for all operations
WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy local files to docker image directory
COPY . .

# run flask app as a module
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

