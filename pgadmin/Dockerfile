FROM dpage/pgadmin4:latest

ARG DB_HOST
ARG DB_PORT
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD

USER root

RUN apk add --no-cache gettext

WORKDIR /pgadmin4
COPY servers-template.json servers-template.json
RUN envsubst < servers-template.json > servers.json

USER pgadmin

ENTRYPOINT [ "/entrypoint.sh" ]
