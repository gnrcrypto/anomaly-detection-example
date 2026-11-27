FROM python:3.12-slim
WORKDIR /app
COPY probe_app.py .
EXPOSE 8080
CMD ["python", "probe_app.py"]
