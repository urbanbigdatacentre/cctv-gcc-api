# glasgow-cctv

# Deployment

> :warning: requires `make` and `docker`

for just the backend:`make deploy-backend`

for the frontend: `make deploy-frontend`

or both: `make deploy`

This will make the image (locally) and push the images to the docker hub.

## IDE Setup

### VSCode

https://code.visualstudio.com/docs/editor/multi-root-workspaces

## tests

> :warning: requires `make`

`make test`

### repo init

> :warning: requires [gh](https://cli.github.com/) and [pre-commit](https://pre-commit.com/)

clone the repo:
`gh repo clone urbanbigdatacentre/glasgow-cctv`

install [pre-commit](https://pre-commit.com/):
`pre-commit install`

### Run tests

> :warning: requires `make` and [poetry](https://python-poetry.org/)

`make test-backend`

### QA

to check for common errors/formats:
`pre-commit run --all-files`

if you want to add/remove more checks, edit
`.pre-commit-config.yaml`
