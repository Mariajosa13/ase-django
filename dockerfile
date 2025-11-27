FROM continuumio/miniconda3


ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app/


RUN conda env create -f environment.yml
RUN echo "source activate django-gis" > ~/.bashrc
ENV PATH /opt/conda/envs/django-gis/bin:$PATH


RUN python manage.py collectstatic --no-input


CMD python manage.py migrate --no-input && gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT