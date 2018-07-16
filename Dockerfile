FROM python:3.6
WORKDIR /app
ADD . /app
RUN pip3 install ansible && apt-get update && apt-get install python3-apt -y
RUN ansible-playbook setup.yml --vault-password-file .vault_pass -vvv
CMD ['./get_tunes.sh']
