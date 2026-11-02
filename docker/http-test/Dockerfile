FROM python:3.12-alpine

RUN apk add --no-cache curl

WORKDIR /app
COPY server.py .

ENV PORT=80
EXPOSE 80

CMD ["python", "-u", "server.py"]
