FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y libvips

COPY . /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
