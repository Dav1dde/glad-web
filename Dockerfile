FROM python:3.11-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/app

RUN pip install --no-cache-dir --use-pep517 \
    glad \
    https://github.com/benoitc/gunicorn/archive/792edf6d9aabcbfb84e76be1d722ac49c32dc027.zip \
    eventlet>0.33.3 \
    flask \
    Flask-AutoIndex \
    raven[flask] \
    lxml

COPY docker/* ./
COPY gladweb gladweb

RUN mkdir temp cache && chmod -R g+w /usr/src/app $VIRTUAL_ENV

ENV PATH="/usr/src/app:${PATH}"
EXPOSE 8080

CMD ["./run.sh"]
