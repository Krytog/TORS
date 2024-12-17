import subprocess
import requests

ID_TO_ADDRESS = {
    1: "localhost:31337",
    2: "localhost:31338",
    3: "localhost:31339",
}

ADDRESS_TO_ID = {
    "localhost:31337": 1,
    "localhost:31338": 2,
    "localhost:31339": 3,
}


def kill_server(id):
    subprocess.run(f"docker-compose stop -t 1 server{id}", shell=True, executable="/bin/bash")

def restart_server(id):
    subprocess.run(f"docker-compose restart server{id}", shell=True, executable="/bin/bash")

def get_leader(id):
    response = requests.get(f"http://{ID_TO_ADDRESS[id]}/leader")
    if response.status_code != 200:
        return None
    return response.json()["leader_id"]

def read(id, key):
    response = requests.get(f"http://{ID_TO_ADDRESS[id]}/data/{key}")
    return response

def create(id, key, value):
    response = requests.post(f"http://{ID_TO_ADDRESS[id]}/create?key={key}&value={value}")
    return response

def update(id, key, value):
    response = requests.put(f"http://{ID_TO_ADDRESS[id]}/update?key={key}&value={value}")
    return response

def delete(id, key):
    response = requests.post(f"http://{ID_TO_ADDRESS[id]}/delete?key={key}")
    return response

def cas(id, key, value, old_value):
    response = requests.patch(f"http://{ID_TO_ADDRESS[id]}/compare_and_swap?key={key}&value={value}&old_value={old_value}")
    return response

def restart():
    subprocess.run("../scripts/complete_restart.sh", shell=True, executable="/bin/bash")
