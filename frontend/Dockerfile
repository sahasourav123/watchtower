FROM python:3.11-slim-bullseye

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install newrelic

COPY . /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV TZ Asia/Kolkata
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

#CMD ["streamlit", "run", "src/Dashboard.py"]
CMD ["newrelic-admin", "run-program", "streamlit", "run", "src/Dashboard.py"]
