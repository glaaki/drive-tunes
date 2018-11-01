FROM python:3.6-alpine
WORKDIR /app
COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt
RUN apk add ffmpeg
COPY ./tunes.py /app
CMD ["python", "tunes.py"]
