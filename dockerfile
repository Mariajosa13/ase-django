FROM continuumio/miniconda3


ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app/


RUN conda env create -f environment.yml



RUN python manage.py collectstatic --no-input


CMD /bin/bash -c "/opt/conda/envs/django-gis/bin/python manage.py migrate --no-input && /opt/conda/envs/django-gis/bin/gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT"