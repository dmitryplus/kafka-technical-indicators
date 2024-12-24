FROM python:3.12-alpine

RUN pip install --user kafka-python-ng tinkoff-investments


ENV PYTHON_TA_LIB_VERSION "0.5"

RUN apk add --no-cache --virtual .build-deps \
        musl-dev \
        linux-headers \
        gcc \
        g++ \
        make \
        curl \
    && cd /tmp \
    && curl -L -O http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -zxf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && pip install setuptools numpy \
    && pip install ta-lib==${PYTHON_TA_LIB_VERSION} \
    && apk del .build-deps \
    && rm -rf /root/.cache \
              /tmp/* \
              /var/cache/apk/* \
              /var/lib/apk/lists/*

COPY ./src .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "./main.py"]