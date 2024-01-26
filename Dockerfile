FROM python:3

RUN apt-get update && apt-get -y install cron
RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
RUN dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb
RUN apt-get update && apt-get install -y mongodb-org

WORKDIR /app

COPY ./src/ ./
COPY cronfile /etc/cron.d/cronfile


RUN chmod 0744 /app/raid-planner.py
RUN chmod 0744 /app/mongo-init.py
RUN python3 -m pip install -r /app/requirements.txt
RUN chmod 0644 /etc/cron.d/cronfile

RUN mkdir -p /data/db /data/configdb \
	&& chown -R mongodb:mongodb /data/db /data/configdb

EXPOSE 27017
CMD ["mongod"]
