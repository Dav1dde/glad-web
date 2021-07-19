FROM python

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/app

RUN pip install --no-cache-dir glad gunicorn==20.1.0 eventlet==0.30.2 flask Flask-AutoIndex raven[flask] lxml

COPY docker/* ./
COPY gladweb gladweb

RUN mkdir temp cache && chmod -R g+w /usr/src/app $VIRTUAL_ENV

ENV PATH="/usr/src/app:${PATH}"
EXPOSE 8080

CMD ["./run.sh"]
