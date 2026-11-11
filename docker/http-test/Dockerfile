FROM python:3.12-alpine

RUN apk add --no-cache curl openssl

WORKDIR /app

# Self-signed cert for the TLS ports (8443, 8444, 8446)
RUN openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
    -keyout /app/key.pem -out /app/cert.pem \
    -subj "/CN=http-test" \
    -addext "subjectAltName=DNS:localhost,DNS:http-test,IP:127.0.0.1"

COPY server.py .

ENV PORTS=80,8080,8089,8443,8444,8446,9000,9001,9100,9102
ENV TLS_PORTS=8443,8444,8446
EXPOSE 80 8080 8089 8443 8444 8446 9000 9001 9100 9102

CMD ["python", "-u", "server.py"]
