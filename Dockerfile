FROM python

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/app

RUN pip install --no-cache-dir git+https://github.com/dav1dde/glad.git@glad2 \
    gunicorn gevent flask Flask-AutoIndex raven[flask] lxml

COPY docker/* ./
COPY gladweb gladweb

RUN mkdir temp cache && chmod -R g+w /usr/src/app $VIRTUAL_ENV

ENV PATH="/usr/src/app:${PATH}"
EXPOSE 8080

CMD ["./run.sh"]
