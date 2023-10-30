FROM python:3.6
COPY ./app/ /app/
WORKDIR /app
RUN pip install mkdocs mkdocs-material gitpython
EXPOSE 80
CMD ["python3", "main.py"]
