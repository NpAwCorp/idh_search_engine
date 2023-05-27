FROM python:3.9

WORKDIR /src

ADD requirements.txt .

ADD ./app .

RUN apt-get update && apt-get install -y netcat

RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

# Set the command to run Streamlit when the container starts
CMD ["streamlit", "run", "main.py", "--server.port", "8501"]