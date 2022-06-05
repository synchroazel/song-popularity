FROM python:3.9.12

WORKDIR /app

COPY handlers/ ./handlers
COPY sql_queries/ ./sql_queries
COPY templates/ ./templates
COPY models/ ./models
COPY flask_app.py .
COPY requirements.txt .
COPY setup.py .

RUN pip3 install -r requirements.txt
RUN pip3 install .

ENV FLASK_APP /app/flask_app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port", "8000"]