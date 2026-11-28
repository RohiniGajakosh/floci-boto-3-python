####Functionality of VPC.Py#####
#1> "Check. if a VPC already been created ? "
#2> If Yes no create, If no Create, i will call AWS to create it--> tag it and then it will save the ID to sate.json


from network.aws_client import get_client
from network.state import load_state, save_state
from botocore.exceptions import ClientError


def create_vpc(config):
    """crate a VPC if it doesn't have one"""
    ec2 = get_client('ec2')
    state = load_state()

    vpc_name = config['vpc']['name']
    vpc_cidr = config['vpc']['cidr']
    tags = config['tags']

    # Already exsists / created before  -->. skip it
    if 'vpc_id' in state:
        try:
            ec2.describe_vpcs(VpcIds=[state['vpc_id']])
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') != 'InvalidVpcID.NotFound':
                raise
            print("VPC was deleted from AWS! Recreating...")
            state.pop('vpc_id')
            state.pop('vpc_name', None)
            save_state(state)
        else:
            print(f"Vpc already exsists (verified on AWS) : {state['vpc_id']}")
            return state['vpc_id']

    # Create a VPC
    response = ec2.create_vpc(CidrBlock=vpc_cidr)
    vpc_id = response['Vpc']['VpcId']
    print(f"Created VPC: {vpc_id}")

    # Wait until the VPC is available
    waiter = ec2.get_waiter('vpc_available')
    waiter.wait(VpcIds=[vpc_id])
    print("VPC is now available")

    # Tag the VPC
    tag_list = [{'Key': 'Name', 'Value': vpc_name}]
    for key, value in tags.items():
        tag_list.append({'Key': key, 'Value': value})
    ec2.create_tags(Resources=[vpc_id], Tags=tag_list)
    print(f"Tagged VPC with: {[t['Key'] for t in tag_list]}")

    # Save to state.json
    state['vpc_id'] = vpc_id
    state['vpc_name'] = vpc_name
    save_state(state)
    print("State saved")

    return vpc_id
