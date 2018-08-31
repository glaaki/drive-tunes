FROM python:3.6-alpine
WORKDIR /app
COPY ./requirements.txt /app
COPY ./tunes.py /app
RUN pip3 install -r requirements.txt
CMD ['python tunes.py']
