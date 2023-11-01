FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry install --with dev

RUN chmod +x backend-start.sh
ENTRYPOINT [ "/app/backend-start.sh" ]
