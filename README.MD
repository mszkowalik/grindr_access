1. create .venv:
python3 -m venv .venv
2. create .env
3. start docker compose:
    docker-compose up -d
4. activate .venv
    source .venv/bin/activate
5. install requirements.txt




Repo init:
1. add submodule:
git submodule add git@github.com:mszkowalik/grindr_access.git


Docker-compose setup:

docker compose up -d --force-recreate --build
docker logs stalkr --follow

