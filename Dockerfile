FROM python:3.10

ENV PYTHONUNBUFFERED 1

ENV APP_HOME /source
WORKDIR $APP_HOME

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:/root/.local/bin"
RUN poetry config virtualenvs.create false

# Install Deps but not tests dep
COPY poetry.lock pyproject.toml /source/
RUN poetry install --no-interaction --no-ansi --no-root --without dev

# Copy Application Code nut not tests
COPY ./app ./app/
RUN poetry install --no-interaction --no-ansi --without dev
