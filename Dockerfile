FROM python:3.14

ENV PIP_ROOT_USER_ACTION=ignore
WORKDIR /var/www/PyDockMate
COPY . .
RUN mkdir -p /var/www/PyDockMate/pydockmate-data

RUN pip install -r requirements.txt  
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
