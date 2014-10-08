FROM ubuntu:14.04
RUN apt-get update -q
RUN apt-get install -qy python-pip
RUN mkdir /src
WORKDIR /src
ADD requirements.txt /src/requirements.txt
RUN pip install -qr requirements.txt
ENTRYPOINT ["./metafig.py"]
