FROM python:3.10.10
RUN apt-get clean \
    && apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential
WORKDIR /app
COPY app/ .
RUN pip3 install -r requirements.txt
COPY start.sh start.sh
COPY nginx.conf /etc/nginx
COPY uwsgi.ini uwsgi.ini
RUN chmod +x start.sh
CMD ["./start.sh"]