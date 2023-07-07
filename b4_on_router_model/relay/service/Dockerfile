FROM ubuntu

RUN apt update

RUN apt install python3 pip -y

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
