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

## Expected vars
ns-servers
```
servers:
    server:
        - name: SERVER-SAMPLE-1
          ipaddress: 10.1.12.101
        - name: SERVER-SAMPLE-2
          ipaddress: 10.1.12.119
        - name: SERVER-SAMPLE-3
          ipaddress: 10.1.12.144
        - name: SERVER-SAMPLE-4
          ipaddress: 10.1.12.145
```

ns-actions
```
    rewriteaction:
          - name: ACTION-SAMPLE-1
            bypasssafetycheck: "NO"
            stringbuilderexpr: "\"/v1/query/assets\""
            type: replace
            target: HTTP.REQ.URL.PATH
    responderaction:
          - name: ACTION-SAMPLE-2
            target: "\"https://\"+HTTP.REQ.HOSTNAME.HTTP_URL_SAFE+HTTP.REQ.URL.PATH_AND_QUERY.HTTP_URL_SAFE"
            bypasssafetycheck: "YES"
            type: redirect
```
