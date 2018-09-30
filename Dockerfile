FROM python:3.7

RUN pip install athenacli
RUN apt-get update && apt-get install -y vim

RUN useradd -ms /bin/bash athena
USER athena
WORKDIR /home/athena

CMD athenacli