FROM python:3.6-slim

WORKDIR /app

ENV PORT=8303 \
    HOST=0.0.0.0 \
    PORT=8301 \
    DEBUG=false \
    NAME=S1 \
    S_HOST=0.0.0.0 \
    S_PORT=8310 \
    S_ENDPOINT='graphql'
COPY . /app/
RUN pip install -r requirements.txt


EXPOSE 8303
CMD [ "python", "app.py" ]