FROM python:3.14-alpine

ARG OC_API_LISTEN_HOST="0.0.0.0"
ARG OC_API_LISTEN_PORT= 4000

RUN apk update
RUN apk upgrade
RUN mkdir -p /app/octools

WORKDIR /app
# STEP 1: Copia els requeriments
COPY requirements.txt .

# STEP 2: Copia la llibreria comuna Odontocare
RUN mkdir -p ./octools
COPY octools/octools ./octools

# STEP 3: Copia l'aplicació
COPY ./src .

# STEP 4: Instalació requeriments
RUN pip install -r requirements.txt

# STEP 5: Configuració i execució applicació
EXPOSE $OC_API_LISTEN_PORT

CMD [ "python3", "api-server.py"] 