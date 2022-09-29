FROM python:3.9-slim-buster

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./ /code

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "80"]