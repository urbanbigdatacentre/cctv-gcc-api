FROM golang:bullseye AS go
RUN GOBIN=/usr/local/bin go install github.com/rogpeppe/go-internal/cmd/testscript@latest
RUN GOBIN=/usr/local/bin go install github.com/go-task/task/v3/cmd/task@latest


FROM python:3.12-slim-trixie AS runner
ENV UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /uvx /bin/
COPY --from=go /usr/local/bin/task /usr/local/bin/task

WORKDIR /app
COPY pyproject.toml uv.lock /app/

RUN uv sync --locked

FROM runner
ADD . /app
ENTRYPOINT [ "task" ]
CMD [ "startserver"]