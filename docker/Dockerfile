FROM python:3.8

WORKDIR /usr/src/app
ENV PATH="/usr/src/app:${PATH}"
EXPOSE 8080

RUN mkdir -p /glad/conf /glad/tmp /glad/cache

RUN pip install --no-cache-dir flask==0.12.5 lxml==4.5.0 gevent==1.4.0 gunicorn==20.0.4 raven==6.10.0 \
    git+https://github.com/sublee/flask-autoindex.git@1e086477c6881c9e40d77359f8a33e47da02b454 \
    git+https://github.com/dav1dde/glad.git@glad2

COPY docker/gunicorn.config.py /glad/conf/
COPY docker/scripts/* .

COPY ./gladweb ./gladweb

RUN groupadd -r glad && useradd --no-log-init -r -g glad glad && chown -R glad:glad ../ && chown -R glad:glad /glad/tmp /glad/cache
USER glad:glad

CMD './start-glad.sh'
