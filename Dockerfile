FROM python:3.14

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /my_blog

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "my_blog.asgi:application", "--host 0.0.0.0", "--port 8000"]