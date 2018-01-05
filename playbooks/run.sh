

echo 
#ansible-playbook -i site.yml -u root --ask-pass test.playbook.yml --tags="$2"  --extra-vars="SVC=$1" $3
ansible-playbook -i site.yml test.playbook.yml --tags="$2"  --extra-vars="SVC=$1" $3
