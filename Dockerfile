FROM python:3.7-alpine
WORKDIR /app
COPY . /app
RUN touch /app/crud.db
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3 crud.py"]
