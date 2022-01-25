# Raspberry Pi Cluster
The main responsibility for this playbook is to gear up the raspberry pis 
so that they have some of my prefered packages, dotfiles, and configures 
a couple applications along the way.  I also used this to learn about 
roles and how to set these up.  If I add more packages to this playbook, 
I will add them here.

## Packages Being Installed
- Vim
- Git
- WGet
- Tmux
- Exuberant-ctags (Needed for a couple vim pluggins)

## Possible Copy Module Issue / Misconfiguration
I think that the tasks below are not working as intended:

```yaml
---
- name: Git clone dotfiles into ~/git/dotfiles
  git:
    repo: https://github.com/retro956/dotfiles.git
    dest: ~/git/dotfiles
    version: master
  environment:
    GIT_TERMINAL_PROMPT: 0

- name: Copy tmux.conf
  copy:
    remote_src: true
    src: ~/git/dotfiles/tmux.conf
    dest: ~/.tmux.conf
    mode: 0755
```
I need to take another look at the copy module that I'm using during 
this playbook.  I have a feeling that I am doing something weird here. 
I'm thinking that all clients are git pulling the dotfiles then they 
are just being copied from the ansible host over to each client.  So if, 
for whatever reason, the files are not available on the host, I'm thinking 
that this playbook will fail.
