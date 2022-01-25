# Docker Swarm Playbook
This ansible playbook allows users to build a docker_swarm on on target clients. 
First, it will install docker.io and docker-compose then init the swarm and join 
the clients via the hosts worker token.

## How to use
You can either modify the playbooks "hosts" to target your clients or you can 
create a hosts group called "pi_cluster".

## Packages that are installed
- docker.io
- docker-compose
