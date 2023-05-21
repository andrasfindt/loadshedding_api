FROM python:3.11
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV FLASK_APP=loadshedding
EXPOSE 21445
ADD eskom-calendar/generated/city-power* eskom-calendar/generated/
COPY loadshedding.py .
ENTRYPOINT ["python3", "loadshedding.py"]
