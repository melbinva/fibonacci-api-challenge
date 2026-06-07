FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir --disable-pip-version-check uv==0.11.19 \
	&& uv sync --frozen --no-dev


FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup --system appgroup && adduser --system --ingroup appgroup --uid 10001 appuser

COPY --from=builder /app/.venv ./.venv

COPY --chown=appuser:appgroup src ./src
RUN chmod -R go-w /app

USER appuser:appgroup

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
