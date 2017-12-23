# Ansible Netscaler
Author: adamlandas@g m.@.l.c0m

## utils/ns_to_yaml.py
* A script that can be used to dump ns.conf to yaml style format
* Example usage: "utils/ns_to_yaml.py -s SOME_SVG" will dump all relivant config for a given serviceGroup
* Requires a copy of ns.conf to be present in script dir.


## Playbooks
Playbooks contain two tasks to apply configuration:
* ansible netscaler modules
* ansible uri modules

Notes:
* ansible uri modules are faster then netscaler modules and a lot faster
* Where no corresponding netscaler module is available, the uri method will be used.

### Ansible netscaler modules
* Not all tasks can be performed by netscaler modules. The uri method is needed in most cases

### Ansible URI modules
* Passing --tags="uri" is both faster, and complete. All actions in vars/sample.yml will be completed if 'uri' is passed


