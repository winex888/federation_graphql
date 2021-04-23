FROM python:3.6-slim

WORKDIR /app

ENV HOST=0.0.0.0 \
    PORT=8310 \
    DEBUG=false \
    NAME=S
COPY . /app/
RUN pip install -r requirements.txt


EXPOSE 8303
CMD [ "python", "app.py" ]