import os
from botocore.exceptions import ClientError
from network.aws_client import get_client
from network.state import load_state, save_state


def create_key_pair(config):
    # Get client and load the state
    ec2 = get_client("ec2")
    state = load_state()

    key_name = config["ec2"]["key_name"]
    os.makedirs("keys", exist_ok=True)
    key_path = os.path.join("keys", f"{key_name}.pem")

    # Guard 1: Check both state AND that the local .pem file actually exists
    if state.get("key_pair_name") == key_name and os.path.exists(key_path):
        print(f"Key pair '{key_name}' already exists in state and at {key_path}")
        return key_name

    # Guard 2: Check if the key already exists in Floci/AWS (e.g., from a previous interrupted run)
    try:
        ec2.describe_key_pairs(KeyNames=[key_name])
        # Key exists in Floci/AWS, but local .pem is missing -> delete so we can regenerate KeyMaterial
        print(f"Key pair '{key_name}' found in AWS/Floci without local .pem. Recreating...")
        ec2.delete_key_pair(KeyName=key_name)
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidKeyPair.NotFound":
            raise

    # Create the key pair and extract PascalCase "KeyMaterial"
    response = ec2.create_key_pair(KeyName=key_name)
    private_key = response["KeyMaterial"]

    # Write private key to keys/<key_name>.pem with owner-only read/write permissions
    with open(key_path, "w") as key_file:
        key_file.write(private_key)
    os.chmod(key_path, 0o600)

    # Record key_name in the state file
    state["key_pair_name"] = key_name
    save_state(state)
    print(f"Created key pair '{key_name}' and saved to {key_path}")
    return key_name