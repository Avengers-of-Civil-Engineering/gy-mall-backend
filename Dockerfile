FROM python:3.9-slim

RUN sed -i "s@http://ftp.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    apt-get install -y apt-transport-https ca-certificates


RUN apt-get update -y && apt-get -y install default-libmysqlclient-dev gcc && \
    mkdir -p /app/gy-mall-backend && \
    pip3 install -i https://mirrors.aliyun.com/pypi/simple \
                asgiref==3.5.0 \
                certifi==2021.10.8 \
                charset-normalizer==2.0.10 \
                Django==3.2.11 \
                django-environ==0.8.1 \
                django-filter==21.1 \
                djangorestframework==3.13.1 \
                djangorestframework-simplejwt==5.0.0 \
                idna==3.3 \
                mysqlclient==2.1.0 \
                Pillow==8.4.0 \
                PyJWT==2.3.0 \
                pytz==2021.3 \
                requests==2.27.1 \
                sqlparse==0.4.2 \
                urllib3==1.26.8 \
                whitenoise==5.3.0 \
                python-dateutil==2.8.2 \
                gunicorn==20.1.0

WORKDIR /app/gy-mall-backend

COPY . /app/gy-mall-backend

EXPOSE 8000

CMD ["python3", "bootstrap.py"]

