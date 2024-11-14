FROM python:3.12.7-alpine
RUN apk --update add build-base bash jpeg-dev zlib-dev python3-dev

WORKDIR /app/demo

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -U \
    pip==24.0 \
    pillow \
    Django==5.1.3 \
    django-bootstrap5 \
    python-dateutil \
    pytz \
    djangorestframework \
    django-vanilla-views

COPY . /app
RUN pip install -e /app
RUN ./manage.py migrate && ./manage.py loaddb

CMD ["python", "manage.py", "runserver", "0:80"]
