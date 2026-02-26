FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run the echo bot example. Override CMD to run your own bot.
CMD ["python", "-m", "examples.echo_bot"]
