docker service create --name registry --publish published=5000,target=5000 registry:2

docker-compose rm -sfv
docker volume prune -f
docker-compose build

docker-compose push
docker swarm leave --force
docker swarm init --force-new-cluster
docker stack deploy --compose-file docker-compose.yaml app
docker service scale app_worker=3 app_customer=3