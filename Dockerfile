FROM python:3.10.2
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000