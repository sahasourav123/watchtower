FROM python:3.13-slim-bullseye

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install newrelic

COPY . /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV TZ Asia/Kolkata
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["newrelic-admin", "run-program", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
