FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . /app/

# Crear el entorno conda
RUN conda env create -f environment.yml

# Ejecutar collectstatic con el Python del entorno
RUN /opt/conda/envs/django-gis/bin/python manage.py collectstatic --no-input

# Comando final (migrate + gunicorn)
CMD /bin/bash -c "\
    /opt/conda/envs/django-gis/bin/python manage.py migrate --no-input && \
    /opt/conda/envs/django-gis/bin/gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT \
"
