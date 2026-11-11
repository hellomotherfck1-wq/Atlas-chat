FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY atlas ./atlas
ENV ATLAS_DB=/data/atlas.db
RUN mkdir -p /data
EXPOSE 8000
CMD ["uvicorn","atlas.main:app","--host","0.0.0.0","--port","8000"]
