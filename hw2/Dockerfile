FROM python:3.10

WORKDIR /main

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Setting default hosts and ports. They will probably be overwritten in docker-compose
ENV MY_ID=1

ENTRYPOINT python3 main.py
