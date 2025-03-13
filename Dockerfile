FROM python:latest

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ARG client_id
ARG secret
ARG google_id
ARG google_secret
ARG cloudinary_name
ARG cloudinary_key
ARG cloudinary_secret
ARG CLOUDINARY_URL
ARG DATABASE_URL
ARG redirect_uri
ARG secret_key
ARG DB_NAME
ARG DB_USER
ARG DB_HOST
ARG DB_PORT
ARG DB_PASSWORD

ENV client_id=${client_id}
ENV DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_PORT=${DB_PORT}
ENV DB_USER=${DB_USER}
ENV CLOUDINARY_URL=${CLOUDINARY_URL}
ENV secret=${secret}
ENV google_id=${google_id}
ENV google_secret=${google_secret}
ENV cloudinary_name=${cloudinary_name}
ENV cloudinary_key=${cloudinary_key}
ENV cloudinary_secret=${cloudinary_secret}
ENV DATABASE_URL=${DATABASE_URL}
ENV redirect_uri=${redirect_uri}
ENV secret=${secret_key}
EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]