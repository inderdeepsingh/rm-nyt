FROM python:3.9

WORKDIR /app

RUN apt-get install -y libvips
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
