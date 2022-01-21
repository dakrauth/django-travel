FROM python:3.8.10-alpine
RUN apk --update add build-base bash jpeg-dev zlib-dev python3-dev

WORKDIR /app/demo

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -U \
    pip \
    pillow \
    choice-enum==1.0.0 \
    Django==3.2.10 \
    django-bootstrap-v5==1.0.8 \
    python-dateutil \
    pytz \
    djangorestframework==3.12.4 \
    django-vanilla-views==3.0.0

COPY . /app
RUN pip install -e /app
RUN ./manage.py migrate && ./manage.py loaddb

CMD ["python", "manage.py", "runserver", "0:80"]
