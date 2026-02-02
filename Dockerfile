# 1. Start with a lightweight Linux version that has Python 3.11 installed
FROM python:3.11-slim

# 2. Set the working directory inside the container to /app
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install the tools inside the container
# We add --no-cache-dir to keep the container small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy source code (main.py, scraper.py, .env) into the container
COPY . .

# 6. Command to run when the container starts
CMD ["python", "main.py"]