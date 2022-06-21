FROM python:3.9-alpine AS init-stage

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
#ENV HTTP_PROXY http://192.168.69.12:3128
#ENV HTTPS_PROXY https://192.168.69.12:3128

COPY ./packages.txt ./pyproject.toml ./poetry.lock* ./requirements.txt /app/

# RUN apt-get install -y -f xargs
# RUN xargs apt-get install -y -f <packages.txt
# RUN tail -f /etc/apk/repositories
# RUN echo -e "http://nl.alpinelinux.org/alpine/v3.16/main\nhttp://nl.alpinelinux.org/alpine/v3.16/community\nhttp://repository.fit.cvut.cz/mirrors/alpine/v3.16/main\nhttp://repository.fit.cvut.cz/mirrors/alpine/v3.16/community\nhttps://dl-cdn.alpinelinux.org/alpine/v3.16/main\nhttps://dl-cdn.alpinelinux.org/alpine/v3.16/community" > /etc/apk/repositories
# RUN echo -e "$(cat repositories.txt)" > /etc/apk/repositories
# RUN tail -f /etc/apk/repositories
RUN apk -U upgrade --no-cache &&  \
    #apk add findutils --allow-untrusted --no-cache && \
    #xargs apk add --allow-untrusted --no-cache <packages.txt && \
    #rm -rf /var/lib/apt/lists/*
	apk add --virtual build-dependencies build-base gcc &&\
    #apk add tzdata &&\
    xargs apk add <packages.txt

ENV PATH="${PATH}:/root/.local/bin"
#FROM python:3.9 AS requirements-stage

#WORKDIR /tmp

#COPY ./pyproject.toml ./poetry.lock* ./requirements.txt /tmp/

# RUN curl -sSL https://install.python-poetry.org -o install-poetry.py

# RUN python install-poetry.py --yes


#RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

#RUN rm requirements.txt

COPY ./ /app/

EXPOSE 80/tcp

CMD nb run --file=bot.py

#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9 AS dependencies-stage

#WORKDIR /app

#COPY --from=init-stage /app/requirements.txt /app/requirements.txt


