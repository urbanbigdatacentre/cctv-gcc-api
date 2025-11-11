FROM golang:bullseye AS go
RUN GOBIN=/usr/local/bin go install github.com/rogpeppe/go-internal/cmd/testscript@latest
RUN GOBIN=/usr/local/bin go install github.com/go-task/task/v3/cmd/task@latest


FROM python:3.12-slim-trixie AS runner
COPY --from=ghcr.io/astral-sh/uv:0.9.6 /uv /uvx /bin/
COPY --from=go /usr/local/bin/task /usr/local/bin/task


FROM runner
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/.cache/uv
ENV UV_PROJECT_ENVIRONMENT=/.cache/.venv
ENV UV_PYTHON_INSTALL_DIR=/.cache/.uv-pythons
WORKDIR /app
ADD . /app
ENTRYPOINT [ "task" ]
CMD [ "startserver"]