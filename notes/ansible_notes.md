# Ansible Notes

## Config Files
Ansible can take in configuration files to help modify how things should 
behave.  When you first install ansible, you may notice that a configuration 
file is not supplied or set to "None".  In order to set a configuration file, 
we must first understand where and how these configuration files are loaded.

### Ansible Configuration File Priority
1. "ANSIBLE_CONFIG"          - Environment variable with a filenme target
2. "./ansible.cfg"           - An ansible.cfg file, in the current directory
3. "~/.ansible.cfg"          - A hidden file in the users home directory
4. "/etc/ansibe/ansible.cfg" - Typically provided through packaged installations

### What config file am I using?
```bash
ansible --version
```
**Results of the above command**

ansible [core 2.11.6]
  config file = None
  ...
  ...

### Which location should I Store my Configuration File?
You can use which ever is best for your case.  I would like to mention that 
the community standard is to use a local ansible.cfg file for each project 
so that you can supply lightweight config files that specifically target 
only what you need it for.

### Example Configuration File
```cfg
# ansible.cfg
[defaults]
inventory = hosts # or hosts.yaml
host_key_checking = False
```

====================================================================================

## Ansible Inventories
```ini
# hosts
# Example Inventory File
[control]
ubuntu-c ansible_connection=local

[ubuntu]
ubuntu[1:3]

[ubuntu:vars]
ansible_become=true
ansible_become_pass=password

[centos]
centos1 ansible_port=2222
centos[2:3]

[centos:vars]
ansible_user=root

[linux:children]
centos
ubuntu
```
OR
```yaml
---
control:
  hosts:
    ubuntu-c:
      ansible_connection: local
centos:
  hosts:
    centos1:
      ansible_port: 2222
    centos2:
    centos3:
  vars:
  ansible_user: root
ubuntu:
  hosts:
    ubuntu1:
    ubuntu2:
    ubuntu3:
  vars:
    ansible_become: true
    ansible_become_pass: password
linux:
  children:
    centos:
    ubuntu:
...
```
OR
```json
{
  "control": {
    "hosts": {
      "ubuntu-c": {
        "ansible_connection": "local"
      }
    }
  },
  "centos": {
    "hosts": {
      "centos1": {
        "ansible_port": 2222
      },
      "centos2": null,
      "centos3": null
    },
    "vars": {
      "ansible_user": "root"
    }
  },
  "ubuntu": {
    "hosts": {
      "ubuntu1": null,
      "ubuntu2": null,
      "ubuntu3": null
    },
    "vars": {
      "ansible_become": true,
      "ansible_become_pass": "password"
    }
  },
  "linux": {
    "children": {
      "centos": null,
      "ubuntu": null
    }
  }
}
```

Inventories are used to keep track of what hosts we have in our ansible 
environment.  This file is typically located in the root directory of 
your ansible project and is called "hosts" or "hosts.yaml".

### ansible_become=true
Setting "ansible_become" to "true" will tell ansible that the user should 
elevate once the secure shell has been established.  When you set this, 
be sure to supply the password needed to elevate with "ansible_become_pass" 
otherwise, you will get an error.

### ansible_connection=local
This will tell ansible that the host is actually local which means that 
ansible does not need to ssh the host listed.

### host[1:3]
This signifies a range.  Ansible will reach out to host1, host2, then host3 
if we specify our hosts in this manner.  Since we are setting the same 
variables, we can simplify our hosts file accordingly.

### [host_group:vars] group
This group will apply variables to all hosts in the group.  If the host has 
a config specified that matches this group, the hosts specified config will 
take precedence over the all:vars group.

### Directory Structure
```bash
#     directory       directory
#     group_vars      host_vars
      - group_1.yaml  - host_1.yaml
```
```yaml
# group_1.yaml
---
ansible_user: root
...

# host_1.yaml
---
ansible_port: 2222
...
```

The best way to structure your playbooks would be to have a directory for 
each inventory variables.  In our example above, we have a group called 
"group_1".  We will create a directory "group_vars" which will contain 
variables for our created groups.  In our example, we will only have one 
group "group_1" which will have a file associated with it "group_1.yaml" 
where we reference the needed variables.  Likewise, we have the same setup 
for variables pertaining to a single host, "host_1.yaml" under the "host_vars" 
directory.

====================================================================================

## Dynamic Inventories
```python
# inventory.py Example
#!/usr/bin/env python3

'''
Dynamic inventory for Ansible in Python
'''
from __future__ import print_function

import argparse
import logging

try:
  import json
except ImportError:
  import simplejson as json

class Inventory(obj):
  def __init__(self, include_hostvars_in_list):
    # configure logger
    # self.configure_logger()

    self.include_hostvars_in_list = include_hostvars_in_list

    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', help='list inventory')
    parser.add_argument('--host', action='store', help='show HOST variables')
    self.args = parser.parse_args()

    if not(self.args.list or self.args.host):
      parser.print_usage()
      raise SystemExit

    self.define_inventory()
    if self.args.list:
      self.print_json(self.list())
    elif self.args.host:
      self.print_json(self.host())

  def define_inventory(self):
    self.groups = {
      "centos": {
        "hosts": ["centos1", "centos2", "centos3"],
        "vars": {
          "ansible_user": "root"
        }
      },
      "control": {
        "hosts": ["ubuntu-c"],
      },
      "ubuntu": {
        "hosts": ["ubuntu1", "ubuntu2", "ubuntu3"],
        "vars": {
          "ansible_become": True,
          "ansible_become_pass": "password"
        }
      },
      "linux": {
        "children": ["centos", "ubuntu"],
      }
    }

    self.hostvars = {
      "centos1": {
        "ansible_port": 2222
      },
      "ubuntu-c": {
        "ansible_connection": "local"
      }
    }

  def print_json(self, content):
    print(json.dumps(content, indent=4, sort_keys=True))

  def list(self):
    # self.logger.into('list executed')
    if self.include_hostvars_in_list:
      merged = self.groups
      merged['_meta'] = {}
      merged['_meta']['hostvars'] = self.hostvars
      return merged
    else:
      return self.groups

  def host(self):
    # self.logger.info(f'host executed for {self.args.host})
    if self.args.host in self.hostvars:
      return self.hostvars[self.args.host]
    else:
      return {}

  def configure_logger(self):
    self.logger = logging.getLogger('ansible_dynamic_inventory')
    self.hdlr = logging.FileHandler('/var/tmp/ansible_dynamic_inventory.log')
    self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    self.hdlr.setFormatter(self.formatter)
    self.logger.addHandler(self.hdlr)
    self.logger.setLevel(logging.DEBUG)

Inventory(include_hostvars_in_list=False)

```
```bash
./inventory.py --host centos1
# {
# "ansible_port": 2222
# }

./inventory.py --host abcdef
# {}
```

Ansible will take the output of "--list" and rerun our script for each host. 
First you will see ansible execute this command "./inventory.py --list" which 
will return a list of hosts.  From there, ansible will iterate through each 
host and run the command "./inventory.py --host ${host}".  From here, we get 
a list of variables to add into our commands.  Then Finally, it will run 
whatever command you asked it to run with ansible (example: ansible all -i inventory.py -m ping).

### Dynamic Inventory Key Requirements
1. Needs to be an executable file. Can be written in any language providing 
that it can be executed from the command line.

2. Accepts the command line options of --list and --host hostname

3. Returns a JSON encoded dictionary of inventory content when used with --list

4. Returns a basic JSON encoded dictionary structure for --host hostname

====================================================================================

## Running Commands
```bash
ansible all -m command -a 'id'
```

The command above will reach out to each host specified, in our case it is the "all" 
group, and will run the command "id" on each host.  This should return which user 
is being used on each host.  Using the Inventory File example above, each centos 
host should return **"centos1 | CHANGED | rc=0 >> uid=0(root) gid=0(root) groups=0(root)"**.

Typically, you will connect to the hosts as your base user then elevate your user 
to root.

### Adding extra variables
```bash
ansible all -m command -a 'id' -e 'ansible_port=2222' -o
```

Adding the "-e" flag will allow you to supply extra variables to your hosts. In the 
example above, we are adding the "ansible_port=2222" variable to all of our hosts. 
Using the configurations listed above, this will result it many errors with the 
exception of our localhost, ubuntu-c, and centos1.  This is due to ssh not being 
needed for the localhost and centos1's port being exposed on 2222 unlike the 
other hosts.

====================================================================================

## Modules
Modules are a way to give ansible functionality on how to interact with the 
targeted hosts.  Keep in mind that most modules can be referenced either by 
their name (file) or their plugin name (ansible.builtin.file). Each module 
will function slightly different so be sure to check out the documentation 
of the module itself.

### Color Notation
When running commands, you may notice a color associated to the output from 
ansible.  These colors will be either Red, Yellow, or Green.

Red = Failure
Yellow = Success with changes
Green = Success no changes

### Ansible-Doc
```bash
# ansible-doc module_name
ansible-doc file
```

### Idempotence
An important though to keep in mind is that our commands should have 
Idempotence which explains that an operation is idempotent, if the 
result of preforming it once, is exactly the same as the result of 
preforing it repeatedly without any intervening actions.  I just wanted 
to add this here to keep this idea in mind when working with ansible 
and modules.

### Setup Module
```bash
# get "facts"
ansible host -m setup
```
This module is automatically called to gather useful information when using 
playbooks as variables about remote targets known as **"facts"**. This 
information can be used during execution.  The setup module can be be executed 
directly by teh ansible command.

### Set_Facts Module
```yaml
hosts: all
tasks:
  - name: Set a fact
    set_fact:
      our_fact: Ansible Rocks!
      ansible_distribution: "{{ ansible_distribution | upper }}"
      
  - name: Show our_fact
    debug:
      msg: "{{ our_fact }}"

  - name: Show ansible_distribution
    debug:
      msg: "{{ ansible_distribution }}"
```
Another Example
```yaml
hosts: all
tasks:
  - name: Set our installation variables for CentOS
    set_fact:
      webserver_application_port: 80
      webserver_application_path: /usr/share/nginx/html
      webserver_application_user: root
    when: ansible_distribution == "CentOS"

  - name: Set our installation variables for Ubuntu
    set_fact:
      webserver_application_port: 8080
      webserver_application_path: /var/www/html
      webserver_application_user: nginx
    when: ansible_distribution == "Ubuntu"

  - name: Show pre-set distribution based facts
    debug:
      msg: "webserver_application_port:{{ webserver_application_port }} webserver_application_path:{{ webserver_application_path }} webserver_application_user:{{ webserver_application_user }}"
```
Using the "set_fact" module, we can, as it would imply, set custom facts 
in our environment.  Above is an example of how we can set a custom fact 
and how we can use this fact.

### File Module
```bash
# touch example
ansible all -m file -a 'path=/tmp/test state=touch'
# create file example
ansible all -m file -a 'path=/tmp/test state=file mode=600'
```
The file module is used for setting attributes of files, creating symlinks 
and directories, or removing files, symlinks, and directories. There are 
many modules that support the same options as the file module, examples 
of these are copy, template, and assemble.  For Windows targets, use the 
win_file module instead.

### Copy Module
```bash
# Copy file from local to target
ansible all -m copy -a 'src=/file/to/copy dest=/path/to/dest'
# Copy file from remote to remote
ansible all -m copy -a 'remote_src=yes src=/file/to/copy dest=/path/to/dest'
```
The copy module is used for copying files, from the local or remote, to 
a location on the remote.  Use the **fetch** module, to copy files from a 
remote target to a local target instead.  If you need variable interpolation 
in the copied files, use teh **template** module.  For windows targets, use 
**win_copy** instead.

### Command Module
```bash
# returns the hostname on target
ansible all -a 'hostname' -o
```
The command module is used for executing remote commands.  This will take the 
command name followed by a list of space-delimited arguments. The given 
command will then be executed on all selected nodes.  The command is not 
processed through the shell, so variables like $HOME and operators will 
not work.  Use the **shell** module if you need those features.  The Windows 
module is **win_command**.

### Service Module
```bash
ansible all -m service -a 'name=nginx state=restarted'
```
Using the Service module, we can manipulate the state of our services running 
on the host.  This is similar to using "systemctl".  You should be able to 
do anything you need with this module just the same way as you would expect 
systemctl to behave.  As always, be sure to check the module documentation 
to see what fields are required.  In this case, the only one that is required 
is the "name" field.

### Pause Module
```yaml
hosts: all
tasks:
  - name: Pause our playbook for 10 seconds
    pause:
      seconds: 10
```
```yaml
hosts: all
tasks:
  - name: Prompt user to verify before continue
    pause:
      prompt: Please check that the webserver is running, press enter to continue
```
We can use this module to halt the playbook from moving forward for a specified 
amount of time.  In our example above, we will wait 10 seconds.  One use case 
for this would be to pause and prompt the user to do something.

### Wait_for
```yaml
hosts: all
tasks:
  - name: Wait for the webserver to be running on port 80
    wait_for:
      port: 80
```
Once again, pretty self explainitory.  This play will wait until it detects 
that port 80 is in use.  Once it detects that port 80 is in use, it will 
continue.

### Assemble Module
```yaml
# playbook.yaml
hosts: all
tasks:
  - name: Assemble conf.d to sshd_config
    assemble:
      src: conf.d
      dest: sshd_config
```
```ini
# conf.d/defaults
Port 22
Protocol 2
ForwardX11 yes
GSSAPIAuthentication no

# conf.d/centos1
Host centos1
  User root
  Port 2222
```
The assemble module allows configuration files to be broken into multiple files 
and then concatenated into the form of a destination file to target host.  This 
is great when an application requires configuration as a single file.  In the 
code example above, we will take all items in the conf.d folder and concat them 
into sshd_config.

### Add Host Module
```yaml
hosts: all
tasks:
  - name: Add centos1 to adhoc_group
    add_host:
      name: centos1
      groups: adhoc_group1, adhoc_group2

hosts: adhoc_group1
tasks:
  - name: Ping all in adhoc_group1
    ping:
```
Add host module will create new inventory groups and targets during runtime. 
This is great for when a host is created during runtime and you would like 
to include it in the playbook.

### Group_by
```yaml
hosts: all
tasks:
  - name: Create group based on ansible_distribution
    group_by:
      key: "custom_{{ ansible_distribution | lower }}"
hosts: custom_centos
tasks:
  - name: Ping all in custom_centos
    ping:
```
Using the group_by module, we can utilize facts to dynamically create associated 
groups.

### Fetch Module
```yaml
hosts: centos
tasks:
  - name: Fetch /etc/redhat-release
    fetch:
      src: /etc/redhat-release
      dest: /tmp/redhat-release
```
Capture files from remote hosts and targets.

### Interesting Packages

#### Package vs Yum and Apt
If you have machines with different operating systems and you would like to 
specify which package manager you should use, you may want to write something 
like this:

```yaml
tasks:
  - name: Install Nginx CentOS
    yum:
      name: nginx
      state: latest
      update_cache: yes
    when: ansible_distribution == "CentOS"

  - name: Install Nginx Ubuntu
    apt:
      name: nginx
      state: latest
      update_cache: yes
    when: ansible_distribution == "Ubuntu"
```

However, there is a better way to do this.  Instead we can use the 
"Package" module like so:

```yaml
tasks:
  - name: Install Nginx
    package:
      name: nginx
      update_cache: yes
      state: latest
```

If we use package, it will decide what the best package manager is needed 
for the job so you do not have to specify which hosts use which specific 
package manager.

====================================================================================

## Ansible Playbooks
### Basic Playbook
```yaml
---
hosts: inventory_hosts                  # Where our play will run
user: unix_user                         # Unix User we wish to use
other_options: values                   # gather_facts: false or something else
tasks:                                  # Start of our Tasks Array
  - name: What the Playbook is Called   # First Task Name
    module:                             # Module to use example file, copy
      module_action: value              # key_value pair example src: /path/to/source
      another_action: another_value     # example dest: /path/to/destination
...
```

The codeblock above is what a very basic playbook might look like.  You would start 
by signifying your hosts that you wish to target, usually using an inventory file. 
Then determine what user you wish to use.  Then you can actually specify variables 
but, I will add a section for this later.  Next comes your tasks, the actions and 
modules you wish to use.  First we give it a name, then specify the module and 
pass any arguments that are needed for the module to function.

### Using Variables
```yaml
---
hosts: centos
user: ansible
gather_facts: false
vars:
  motd: "Welcome to CentOS Linux - Ansible Rocks\n"
tasks:
  - name: "Copying MOTD to '{{ hosts }}'"
    copy:
      content: "{{ motd }}"
      dest: /etc/motd
...
```
```bash
ansible-playbook motd.yaml                           # Default Command
ansible-playbook motd.yaml -e 'motd="Changed MOTD!"' # Customized MOTD
```

### Using Custom Variables
```yaml
hosts: linux
tasks:
  - name: Make Facts Dir
    file:
      path: /home/ansible/facts.d
      recurse: yes
      state: directory
      owner: ansible

  - name: Copy Fact 1
    copy:
      src: facts.d/getdate1.fact
      dest: /home/ansible/facts.d/getdate1.fact
      owner: ansible
      mode: 0755

  - name: Reload Facts
    setup:
      fact_path: /home/ansible/facts.d

  - name: Show IP Address
    debug:
      msg: "{{ ansible_default_ipv4.address }}"

  - name: Show Custom Fact 1
    msg: "{{ ansible_local.getdate1.date }}"
```
```bash
# getdate1.fact
#!/bin/bash
echo {\""date\"" : \""`date`\""}
```

You can also add custom variables to your facts.  The above code here 
will copy your custom facts from your local machine over to all other 
hosts specified at target destination.  Once the directory is created 
and your files are copied, we can reload our facts using the copied 
files.  Once we do this, our custom facts will be accessable under 
ansible_local.

### Adding Handlers
```yaml
---
hosts: centos
user: ansible
gather_facts: false
vars:
  motd: "Welcome to CentOS Linux - Ansible Rocks\n"
tasks:
  - name: "Copying MOTD to '{{ hosts }}'"
    copy:
      content: "{{ motd }}"
      dest: /etc/motd
    notify: MOTD changed
handlers:
  - name: MOTD changed
    debug:
      msg: The MOTD was changed
...
```

Handlers are used to resolve or "handle" the transition after a task. 
In our example above, we are creating a key value pair called "notify" 
with the value of "MOTD changed".  This will be the signal we will send 
when the task is resolved.  Then we create a new section called "handlers" 
in which we set the name equal to the notify field.  This is how we are 
mapping the task to a handler.  Also note that the handler is only used 
when something changes.  If we get an "ok" signal, the handler will not 
be used.

### Good Habbits To Have
One really good habbit to develop would be to never assume that a task 
was successful and always create a handler to check and ensure that 
everything went ok as intented.  For example, we may restart a service 
but, that service could have failed after the restart.  So, it is always 
best practice to create a handler that will double check if the service 
came back up or that the task was completed and everything is good to go. 
Handlers are your friend!

Another handler example:
```yaml
hosts: all
tasks:
  - name: Restart Nginx
    service:
      name: nginx
      state: restarted
    notify: Check HTTP Service
handler:
  - name: Check HTTP Service
    uri:
      url: http://{{ ansible_default_ipv4.address }}
      status_code: 200
```

This is always better than just assuming that the nginx service is 
back up after the restart.  There is a possibility that we passed a 
faulty config to NGINX and we would never know that it didn't come back 
up properly without this check.

====================================================================================

## Templating with Jinja2
Jinja2 is a templating language that is used in many different locations. 
Ansible does support this templating language so you may see elements 
of it from time to time.  In our previous examples, we were using Jinja2 
to inject variables into our playbooks with "{{ variable }}".

### If / elif / else statements
```yaml
# playbook.yaml
---
hosts: all
tasks:
  - name: Ansible Jinja2 if
    debug:
      msg: >
          --== Ansible Jinja2 if statement ==--
          {% if ansible hostname == "ubuntu-c" -%}
            This is ubuntu-c
          {% elif ansible_hostname == "centos1" -%}
            This is centos1 with it's modified SSH Port
          {% else -%}
            This is gold old {{ ansible_hostname }}
          {% endif %}
...
```

### is defined
```yaml
hosts: all
tasks:
  - name: Ansible Jinja2 if variable is defined
    debug:
      msg: >
          --== Ansible Jinja2 if variable is defined ==--
          {% if example_variable is defined -%}
            example_variable is defined
          {% else -%}
            example_variable is not defined
          {% endif -%}
```

### Setting a Variable
```yaml
hosts: all
tasks:
  - name: Ansible Jinja2 if variable is defined
    debug:
      msg: >
          --== Ansible Jinja2 if variable is defined ==--
          {% set example_variable = 'defined' -%}

          {% if example_variable is defined -%}
            example_variable is defined
          {% else -%}
            example_variable is not defined
          {% endif -%}
```

### For Loops
```yaml
hosts: all
tasks:
  - name: Ansible Jinja2 if variable is defined
    debug:
      msg: >
          --== Ansible Jinja2 for loop ==--
          {% for entry in ansible_interfaces -%}
            Interface entry {{ loop.index }} = {{ entry }}
          {% endfor %}
```

### Ranges
```yaml
hosts: all
tasks:
  - name: Ansible Jinja2 for range
    debug:
      msg: >
          --== Ansible Jinja2 for range ==--
          {% for entry in range(1, 11) -%}
            {{ entry }}
          {% endfor %}
```

### Break and Continue
```yaml
hosts: all
tasks:
  - name: Ansible Jinja2 for range, reversed
    debug:
      msg: >
          --== Ansible Jinja2 for range, reversed ==--
          {% for entry in range(10, 0, -1) -%}

            {% if entry == 5 -%}
              {% break %}
            {% endif -%}

            {{ entry }}

          {% endfor %}
```

====================================================================================

## Register and When
```yaml
# playbook.yaml
hosts: linux
tasks:
  - name: Exploring register
    command: hostname -s
    register: hostname_output

  - name: Show hostname_output
    debug:
      var: hostname_output
```
```bash
ansible-playbook playbook.yaml
```

Register is used to keep track of the output that something might give off.  For 
example, we may want to run the command "ansible all -a 'hostname -s' -o", if the 
command is ran in the terminal, then it should return back with the hostname of the 
container.  However, when we decide to do this in a playbook, it will signify that 
a change was made but, it will not display any information.  This is where the 
register command comes in play.  We can register the output of the "hostname -s" 
command then display it using debug.  After running the command above, we will get 
a large amount of data. We can further specify what exactly we wish to see with the 
playbook below.

```yaml
# playbook.yaml revised
# We are only interested in the "stdout" key.
hosts: linux
tasks:
  - name: Exploring register
    command: hostname -s
    register: hostname_output

  - name: Show hostname_output from stdout
    debug:
      var: hostname_output.stdout
```

### More Examples
```yaml
hosts: all
tasks:
  - name: Exploring register
    command: hostname -s
    when:
      - ansible_distribution == "CentOS"
      - ansible_distribution_major_version | int >= 8
    register: command_register

  - name: Install patch when changed
    yum:
      name: patch
      state: present
    when: command_register is changed
```

====================================================================================

## Ansible Loops

### with_item
```yaml
# Playbook Before Loops
hosts: linux
tasks:
  - name: Configure a MOTD
    copy:
      content: "Welcome to {{ ansible_distribution }} Linux - Ansible Rocks\n"
      dest: /etc/motd
    notify: MOTD changed

handlers:
  - name: MOTD changed
    debug:
      msg: The MOTD was changed
```
```yaml
# Playbook with Loops
hosts: linux
tasks:
  - name: Configure a MOTD
    copy:
      content: "Elcome to {{ item }} Linux - Ansible Rocks!\n"
      dest: /etc/motd
    notify: MOTD changed
    with_items:
    - CentOS
    - Ubuntu
    when: ansible_distribution == item

handlers:
  - name: MOTD changed
    debug:
      msg: The MOTD was changed
```
```yaml
hosts: linux
tasks:
  - name: Creating user
    user:
      name: "{{ item }}"
      #state: absent
    with_items:
      - james
      - hayley
      - lily
      - anwen
```
```bash
# Check if the users were created successfully
ssh host tail -5 /etc/passwd
```

### with_dict
```yaml
hosts: linux
tasks:
  - name: Creating user
    user:
      name: "{{ item.key }}"
      comment: "{{ item.value.full_name }}"
      #state: absent
    with_dict:
      james:
        full_name: James Doe
      hayley:
        full_name: Hayley Doe
      lily:
        full_name: Lily Doe
      anwen:
        full_name: Anwen Doe
```

### with_subelements
```yaml
hosts: linux
tasks:
  - name: Creating user
    user:
      name: "{{ item.1 }}"
      comment: "{{ item.1 | title }} {{ item.0.surname }}"
    with_subelements:
      - family:
        surname: Doe
        members:
          - james
          - hayley
          - lily
          - anwen
      - members
```
```yaml
hosts: linux
tasks:
  - name: Creating user
    user:
      name: "{{ item.1 }}"
      comment: "{{ item.1 | title }} {{ item.0.surname }}"
      password: "{{ lookup('password', '/dev/null length=15 chars=asci_letters,digits,hexdigits,punctuation') | password_hash('sha512') }}"
    with_subelements:
      -
        - surname: Doe
          members:
            - james
            - hayley
            - lily
            - anwen
        - surname: Jalba
          members:
            - ana
        - surname: Angne
          members:
            - abishek
      - members

```

====================================================================================
## Includes and Imports
### Basic Include
```yaml
# play1_task1.yaml
---
hosts: all
tasks:
  - name: Play 1 - Task 1
    debug:
      msg: Play 1 - Task 1
  - include_tasks: play1_task2.yaml
...
# play1_task2.yaml
---
- name: Play 1 - Task 2
  debug:
    msg: Play 1 - Task 2
...
```

Using "include_tasks", we can include tasks from other files to run an action.  In 
the example above, we have a play that uses debug.msg to state "Play 1 - Task 1" but 
then includes task "play1_task2.yaml" which will return the message "Play 1 - Task 2". 
These tasks will be ran in the order that you included them in.

### Import VS Include
When running import, your code is processed as the playbook is being parsed.  However 
in the case of include, the file is processed at playbook execution.  The "when" is 
slightly changed in both situations.  In the case of import, "when" statements apply 
to all individual tasks at task point of execution.  Include's "when" statement 
applies to all tasks at initial point of execution.  If you have a task which will 
create any information for the main playbook to handle, you should use import.

====================================================================================

## Ansible Vault
Ansible Vault is a tool that will encrypt and decrypt variables and files to be used 
later.  This is great for any type of sensitive data that you do not want to reveal.

### How this works
```bash
# ansible-vault encrypt_string --ask-vault-pass --name 'key' 'value'
ansible-vault encrypt_string --ask-vault-pass --name 'ansible_become_pass' 'password'
# Another way to do this. If you do this, be sure to double check formatting
ansible-vault encrypt_string --ask-vault-pass --name 'ansible_become_pass' 'password' >> vars.yaml
```
```yaml
# Example group var yaml
---
ansible_become: true
ansible_become_pass: !vault |
          $ANSIBLE_VAULT;1.1'AES256
          129873198273196489641278319827319048689756124891273094712356102398741902374
          908172487213984718276498123648917263481276390487123904871239486712390834134
          394786239485234502394560239456203948572376592837450293847502346589234590278
          12341
```
When running the command above, you should be asked for a vault password.  This 
password is used similarly to a "passphrase". This will return your ansible_vault 
encrypted key value pair.  You will then need to add this data to your group_var 
or host_var files so that it can be used for later. 

### How to use Vault after creating a vault password
```bash
ansible ubuntu -m ping -o --ask-vault-pass
```
Adding the flag "--ask-vault-pass", you should then be asked for the vault password 
associated with the encrypted data.  This is where you type the password that you 
set when encrypting your information. 

### Using encrypted files
```yaml
# encrypt_me.yaml before encryption
---
ansible_become_password: password123
...
```
```bash
ansible-vault encrypt encrypt_me.yaml
```
```yaml
# encrypt_me.yaml after encryption
$ANSIBLE_VAULT;1.1;AES256
891726348917236491827341897634891673428912763489127348917263489176348971647
123894710293741237689756349087523789652893746512390741290378523489756349011
012987412908371278364192837659872619082734109283741562389174023984665123897
```
```yaml
# vault_test_playbook.yaml
- hosts: all
  vars_files:
    - encrypt_me.yaml
  tasks:
    - name: Show ansible_become_password
      debug:
        var: ansible_become_password
```
```bash
# Final command to run
# remember that the vault pass is what we set when encrypting our file
ansible-playbook vault_test_playbook.yaml --ask-vault-pass
```

### Decrypting a file
```bash
ansible-vault decrypt file_to_decrypt
```
This will return the file back to it's original state. Once again, you will need 
the vault password to preform this action.

### Re-encrypt file to cycle vault password
```bash
ansible-vault rekey file_to_rekey
```

### Use a password file
```yaml
# Example by viewing encrypted file
ansible-vault view --vault-password-file password_file encrypted_file
# Enter password via a prompt
ansible-vault view --vault-id @prompt encrypted_file
```
When using the prompt, you will type the literal characters "@prompt" value 
for the "--vault-id" flag.

### vault-id flag
name_of_vault@[filename|prompt]  
The vault-id flag can take arguments using the format above. If you do not have 
a name associated to the vault, you can leave that field blank.

### Named Vaults
```bash
# ansible-vault encrypt --vault-id vault_name@[password_file | prompt] file_to_encrypt.yaml
ansible-vault encrypt --vault-id vars@prompt file_to_encrypt.yaml
# alternatively we can run this
ansible-vault encrypt_string --vault-id ssh@prompt --name 'ansible_become_pass' 'password' >> group_vars/group_var_file
```
```yaml
# After encryption
$ANSIBLE_VAULT;1.2;AES256;vars
      309812734091827340198273401982401928401897401978234091827349081234091734098
      029865189023490182734871264891726349817234908162389765012937409182374906235
      123904712378641892356983475902384752893652304578029867527896345029834509827
      234612394567239845623789623489723048578347575757485728942939408723495872345
```
```bash
# Running a playbook using the vars vault and ssh vault
ansible-playbook --vault-id vars@prompt --vault-id ssh@prompt vault_playbook.yaml
```

### Encrypting Playbooks
```bash
# Encrypt playbook
ansible-vault encrypt --vault-id playbook@prompt vault_playbook.yaml

# Run vault_playbook.yaml using the vault id "playbook" and prompt for password
ansible-vault --vault-id playbook@prompt vault_playbook.yaml
```
I just wanted to include the fact that you can also encrypt your playbooks.

====================================================================================

## Ansible Tags
Tags are primarily used to run specific sections of your playbook without having 
to run the entire playbook.

### Tags With a Previous Example
```yaml
# playbook.yaml
- hosts: linux

  # Optional Playbook Tag
  #tags:
  #  - webapp

  vars_files:
    - vars/logos.yaml

  tasks:
    - name: Install EPEL
      yum:
        name: epel-release
        update_cache: yes
        state: latest
      when: ansible_distribution == "CentOS"
      tags:
        - install-epel

    - name: Install Nginx
      package:
        name: nginx
        state: latest
      tags:
        - install-nginx

    - name: Restart nginx
      service:
        name: nginx
        state: restarted
      notify: Check HTTP Service
      tags:
        - restart-nginx
        
    - name: Template index.html-easter_egg.j2 to index.html on target
      template:
        src: index.html-easter_egg.j2
        dest: "{{ nginx_root_location }}/index.html"
        mode: 0644
      tags:
        - deploy-app

    - name: Install unzip
      package:
        name: unzip
        state: latest

    - name: Unarchive playbook stacker game
      unarchive:
        src: playbook_stacker.zip
        dest: "{{ nginx_root_location }}"
        mode: 0755
      tags:
        - deploy-app

  handlers:
    - name: Check HTTP Service
      uri:
        url: http://{{ ansible_default_ipv4.address }}
        status_code: 200

```
```bash
# Install specific tags
ansible-playbook playbook.yaml --tags "install-epel,restart-nginx"

# Everything but specified tag
ansible-playbook playbook.yaml --skip-tags "install-epel"

# Run everything
ansible-playbook playbook.yaml --tags "all"
```

### Tagging Entire Playbooks
Using the example above, you will see "Optional Tags" commented out.  If we 
uncomment this, we can refer to the entire playbook by it's tag.  However if 
we set things up this way, the setup module will not run the "gather facts" 
portion.  So if you have a playbook that relies on these facts and you have 
to put a tag on the playbook, you will have to create an empty playbook. 
This will look something like this:

```yaml
- hosts: linux
- hosts: linux
  tags:
    - webapp
  vars_files:
    - vars/logo.yaml
  tasks:
    - name: blahblahblah
```

This will ensure that the gather facts process actually takes play when it 
reads "hosts: linux" initially.

### Tagging Always
When we tag something as "always", the play will always happen no matter 
what tag we call or how we run the playbook.  This can be useful for 
something like "nginx" or "apache" where any changes we make, we most 
likely want to restart the nginx or apache service so that these changes 
can take effect.

### Other Special Tags
```bash
# Run only tagged tasks
ansible-playbook playbook.yaml --tags "tagged"

# Run only untagged tasks
ansible-playbook playbook.yaml --tags "untagged"

# Run every task
ansible-playbook playbook.yaml --tags "all"
```

### Tags and Importing / Including Tasks
```yaml
- hosts: all
  tasks:
    - include_tasks: include_tasks.yaml
      tags:
        - include_tasks
    - import_tasks: import_tasks.yaml
      tags:
        - import_tasks
- import_playbook:
  tags:
    - import_playbook
```

====================================================================================

## Roles
### Creating the Role Skeleton
```bash
ansible-galaxy init $role
```

### Role Typical File Structure
```python
# Role file structure
example-role/
|--README.md
|--defaults/
|  |--main.yaml
|--files/
|  |--handlers/
|     |--main.yaml
|--meta/
|  |--main.yaml
|--tasks/
|  |--main.yaml
|--templates/
|--tests/
|  |--inventory
|  |--test.yaml
|--vars
   |--main.yaml
```

\newpage
