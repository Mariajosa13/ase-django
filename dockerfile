FROM continuumio/miniconda3

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/

# Crear entorno conda
RUN conda env create -f environment.yml && \
    echo "conda activate django-gis" >> ~/.bashrc

# Todas las instrucciones siguientes ejecutan dentro del entorno
SHELL ["/bin/bash", "--login", "-c"]

RUN conda activate django-gis && \
    python manage.py collectstatic --no-input

CMD /bin/bash -c "source activate django-gis && python manage.py migrate --no-input && gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT"
