FROM python:3.7

# should probably create a user to not run as root

RUN pip install --upgrade pip
WORKDIR /usr/src/app 
COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x boot.sh

EXPOSE 5017
ENTRYPOINT ["./boot.sh"]
