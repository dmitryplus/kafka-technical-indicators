FROM python:3.12-alpine

RUN pip install --user tinkoff-investments

COPY ./src .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "./main.py"]