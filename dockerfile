FROM continuumio/miniconda3


ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app/


RUN conda env create -f environment.yml
RUN echo "source activate django-gis" > ~/.bashrc


RUN python manage.py collectstatic --no-input


CMD conda run -n django-gis python manage.py migrate --no-input && conda run -n django-gis gunicorn ASEproject.wsgi:application --bind 0.0.0.0:$PORT