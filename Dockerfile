FROM python:3.14-slim

ENV PIP_ROOT_USER_ACTION=ignore
WORKDIR /var/www/PyDockMate
COPY . .
RUN mkdir -p /var/www/PyDockMate/pydockmate-data

RUN pip install -r requirements.txt  
RUN python manage.py migrate

CMD ["/bin/sh","-c", "python manage.py migrate && python -u manage.py runserver 0.0.0.0:8000"]
