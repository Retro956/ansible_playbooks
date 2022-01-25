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

## Stuff to do
### Remove hardcoded IPADDRs
Move private ip addresses either to host_vars or find another smart way to 
take a look at the ip addresses.  It would probably make more sense to use 
a variable defined by setup to do this.  This would be a little more dynamic 
so that if the host ipv4 addr changes, it doesn't break the playbook.  

### Use docker_swarm module over shell module
I noticed that there is a docker_swarm module that I could most likely use 
for this playbook instead of using the shell module.  I will have to take a 
look at this module sometime to convert this playbook.

### I should probably add handlers
It might be a good idea to add handlers to this playbook so that I can make 
sure that the shell commands ran properly.  As of right now, nothing is really 
notifying ansible that the commands were successful.  So if there are to be 
any errors along the way that ansible doesn't catch, I would have no idea.
