# Playbooks
Author: Author: adamlandas@g m.@.l.c0m
Sample playbooks to be used by dumps from ns_to_yaml.py


## Example usages:
### URI method
Uses uri instead of built in netscaler modules
```
ansible-playbook -i site.yml sample.playbook.yml -u root --ask-pass --tags="uri"
```

### netscaler method
Uses netscaler modules first, uri when there is not a netscaler method:
```
ansible-playbook -i site.yml sample.playbook.yml -u root --ask-pass --tags="module"
```
