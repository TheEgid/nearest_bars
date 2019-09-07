FROM python:3.7.4

RUN apt-get update && apt-get install -qy \
    apt-utils \
    python3-numpy \
    python3-psycopg2 \
    python3-pip

EXPOSE 8080
WORKDIR /opt
COPY . /opt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py", "Москва Кленовый бульвар 9", "--test"]
