FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/

RUN conda env create -f environment.yml

SHELL ["/bin/bash", "--login", "-c"]

RUN conda activate django-gis && \
    python manage.py collectstatic --no-input

CMD ["bash", "-c", "python manage.py migrate --no-input && gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT"]
