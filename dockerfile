FROM continuumio/miniconda3


ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app/


RUN conda env create -f environment.yml
RUN echo "source activate django-gis" > ~/.bashrc


RUN python manage.py collectstatic --no-input


CMD /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate django-gis && python manage.py migrate --no-input && gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT"