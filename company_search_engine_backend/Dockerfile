FROM python:3.9

WORKDIR /src

ADD requirements.txt .

ADD ./app .

RUN apt-get update && apt-get install -y netcat

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD ["gunicorn", "-w", "4", "-t" , "0", "-k",  "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--access-logfile", "-", "main:app"]