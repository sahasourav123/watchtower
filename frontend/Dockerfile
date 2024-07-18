FROM python:3.11-slim-bullseye

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV TZ Asia/Kolkata
ENV PYTHONPATH "${PYTHONPATH}:/app/src"
VOLUME ["/data"]
CMD ["streamlit", "run", "src/Home.py"]
