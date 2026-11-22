.PHONY: rebuild-worker

rebuild-worker:
	docker compose down
	-docker ps -aq --filter ancestor=universal-worker | xargs -r docker rm -f
	docker images -q universal-worker | xargs -r docker rmi -f
	docker build -f ./generic_framework/Dockerfile.worker -t universal-worker ./generic_framework
	docker compose up -d --build
	docker image inspect universal-worker >/dev/null
