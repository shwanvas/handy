FROM python:3.8.10
ADD . /handy
WORKDIR /handy
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD gunicorn app:app