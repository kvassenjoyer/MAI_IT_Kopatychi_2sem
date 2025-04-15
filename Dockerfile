FROM python:3.10

# install
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
# expose server port
EXPOSE 8000
COPY . .

# start app
CMD [ "python3", "core/manage.py", "runserver", "0.0.0.0:8000" ]