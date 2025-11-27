FROM continuumio/miniconda3

# Evitar preguntas en instalación
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/

# Crear entorno conda y activarlo
RUN conda env create -f environment.yml && \
    echo "conda activate django-gis" >> ~/.bashrc

# Activar entorno para siguientes RUN
SHELL ["/bin/bash", "--login", "-c"]

# Instalar dependencias de Django
RUN conda activate django-gis && \
    python -m pip install gunicorn && \
    python manage.py collectstatic --no-input

# Comando final
CMD /bin/bash -c "source activate django-gis && python manage.py migrate --no-input && gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT"
