FROM python:2.7
ADD . /app
WORKDIR /app
EXPOSE 9005
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]
