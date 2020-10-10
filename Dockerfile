FROM python:3.9.0

RUN apt-get update && apt-get install -qy \
    apt-utils \
    python3-numpy \
    python3-psycopg2 \
    python3-dotenv

RUN pip install --upgrade pip
RUN python -m pip install folium

EXPOSE 80
WORKDIR /opt
COPY . /opt

RUN pip install -r requirements.txt

CMD ["python", "main.py", "Москва Кленовый бульвар 9"]
