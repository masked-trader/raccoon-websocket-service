FROM python:3.11 AS python-base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry:
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PATH="$PATH:/root/.local/bin"

RUN pip install pipx
RUN pipx install poetry

FROM python-base as builder-base

WORKDIR /workspace

COPY pyproject.toml \
    poetry.lock \
    /workspace/

RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY src/ /workspace/src/

COPY files/entrypoint.sh \
    files/wait-for-it.sh \
    /

RUN chmod 775 \
    /wait-for-it.sh \
    /entrypoint.sh \
    /workspace/src/main.py

RUN mv /wait-for-it.sh /bin/wait-for-it

FROM builder-base AS development

WORKDIR /workspace

RUN poetry install --with dev --no-root --no-interaction --no-ansi

ENTRYPOINT ["/entrypoint.sh"]
CMD ["poetry", "run", "python", "src/main.py"]

FROM builder-base AS production

WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh"]
CMD ["poetry", "run", "python", "src/main.py"]
