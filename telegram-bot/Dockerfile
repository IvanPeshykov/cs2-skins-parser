FROM python:3.10.2-slim

WORKDIR /app

# Copy only the bot-related files
COPY . .

COPY requirements.txt .

# Install the required dependencies (bot dependencies)
RUN pip install -r requirements.txt

EXPOSE 8000

# Start the FastAPI server for bot communication
CMD ["python", "bot.py"]