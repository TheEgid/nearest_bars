FROM python:3.9.0

RUN apt-get update && apt-get install -qy \
    apt-utils \
    python3-numpy \
    python3-psycopg2 \
    python3-pip

EXPOSE 8080
WORKDIR /opt
COPY . /opt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py", "Москва Кленовый бульвар 9", "--test"]
