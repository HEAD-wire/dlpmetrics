FROM python:3.11-buster
# Dockerfile
RUN pip install --upgrade pip

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install libpq-dev

RUN useradd -m dlp
USER dlp
WORKDIR /dlp

COPY --chown=dlp:dlp ./worker/requirements.txt requirements.txt
RUN ls
RUN pip install --user -r requirements.txt

COPY  --chown=dlp:dlp worker .
ADD  --chown=dlp:dlp pkg pkg

CMD ["python", "./main.py"]