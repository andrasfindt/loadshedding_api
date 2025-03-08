FROM python:3.13
WORKDIR /code
COPY requirements.txt .
COPY citypower.co.za.pem /etc/ssl/certs/
RUN update-ca-certificates
RUN pip install -r requirements.txt
ENV FLASK_APP=loadshedding
EXPOSE 21445
ADD client/* client/
COPY *.py .
ENTRYPOINT ["python3", "loadshedding.py"]
