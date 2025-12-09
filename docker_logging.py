import docker

client = docker.from_env()

containers = client.containers.get('PostgreSQL')
logs_from_container = container.logs(cpu_percent) 

containers_list = client.containers.list()

for line in logs_from_container.logs():
    print(line.strip())


