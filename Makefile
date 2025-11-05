GIT_SHA_FETCH := $(shell git rev-parse HEAD | cut -c 1-7)
export GIT_SHA_FETCH

.PHONY: test-backend test

test: test-backend

deploy: build-image-backend build-image-frontend
# dont forget to login to docker hub first with rw access
	docker push ubdc/glasgow-cctv-backend:${GIT_SHA_FETCH}
	docker push ubdc/glasgow-cctv-frontend:${GIT_SHA_FETCH}
	@echo "Deployed to docker hub"
	@echo "Now edit the deployment files to use the new image"
	@echo ubdc/glasgow-cctv-frontend:${GIT_SHA_FETCH}
	@echo ubdc/glasgow-cctv-backend:${GIT_SHA_FETCH}

deploy-frontend: build-image-frontend
	docker push ubdc/glasgow-cctv-frontend:${GIT_SHA_FETCH}
	@echo "Deployed to docker hub"
	@echo "Now edit the deployment files to use the new image"
	@echo ubdc/glasgow-cctv-frontend:${GIT_SHA_FETCH}

deploy-backend: build-image-backend
	docker push ubdc/glasgow-cctv-backend:${GIT_SHA_FETCH}
	@echo "Deployed to docker hub"
	@echo "Now edit the deployment files to use the new image"
	@echo ubdc/glasgow-cctv-backend:${GIT_SHA_FETCH}

build-image-backend:
	docker build -t ubdc/glasgow-cctv-backend:${GIT_SHA_FETCH} ./projects/backend

build-image-frontend:
	docker build -t ubdc/glasgow-cctv-frontend:${GIT_SHA_FETCH} ./projects/frontend/

test-frontend:
	@echo "Running frontend-tests..."

test-backend:
	@echo "Running backend-tests..."
	poetry install --no-root -C ./projects/backend/
	cd ./projects/backend/ && poetry run pytest -vvv --cov=app --cov-report=term-missing --cov-fail-under=80 --cov-config=.coveragerc --cov-report=html:../../cov_html --cov-report=annotate
