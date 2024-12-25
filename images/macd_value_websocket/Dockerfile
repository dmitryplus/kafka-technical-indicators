FROM python:3.12-alpine

RUN pip install --user kafka-python-ng websockets

COPY ./src .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "./main.py"]