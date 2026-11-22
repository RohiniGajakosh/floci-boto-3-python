import os 
from network.aws_client import get_client
from network.state import load_state, save_state

def create_key_pair(config):
    # get client and load the state 
    ec2 = get_client("ec2", config)
    state = load_state()

    #Guard: In case the key is present in state file , print it exists and return

    if "key_pair_name" in state:
        print(f"key pair {state['key_pair_name']} already exists in state")
        return state['key_pair_name']
    
    key_name = config["ec2"]["key_name"]

    #call ec2.create_key_pair(KeyName = key_name) and keep the response
    response = ec2.create_key_pair(KeyName=key_name) 

    #The private key test is response["KeyMaterial"]
    private_key = response["keyMaterial"]

    #Create keys/ directory if needed then write keys to key/<key_name>
    os.mkdirs("keys", exist_ok=True)
    key_path = os.path.join("keys", f"{key_name}.pem")
    with open(key_path, "w") as key_file:
        key_file.write(private_key)

    # restricting file permission to owner read/write only 
    os.chmod(key_path , 0o600)

    #record key_name in the state file
    state["key_pair_name"] = key_name
    save_state(state)