# Ansible netscaler playbooks

## utils/ns_to_yaml.py
A script that can be used to dump ns.conf to yaml style format

## Playbooks
Playbooks contain two tasks to apply configuration:
* ansible netscaler modules
* ansible uri modules

ansible uri modules are faster then netscaler modules and a lot faster
