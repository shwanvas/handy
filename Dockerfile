FROM python:3.8.10
ADD . /handy
WORKDIR /handy
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0"]