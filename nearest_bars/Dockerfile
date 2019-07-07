FROM debian:buster

RUN apt-get clean && apt-get update
RUN apt-get install -qy apt-utils
RUN apt-get install -qy python3-numpy
RUN apt-get install -qy python3-psycopg2
RUN apt-get install -qy python3-pip

EXPOSE 8080
WORKDIR /opt
COPY . /opt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py", "Москва Кленовый бульвар 9", "--test"]
