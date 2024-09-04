FROM python:3.10-slim

ENV BASE_DIR=/code
COPY . ${BASE_DIR}
WORKDIR ${BASE_DIR}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]