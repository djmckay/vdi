import boto3
import json
import base64
import os

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    # Load Ansible playbook repo and config
    ansible_repo_url = "https://github.com/your-org/your-ansible-playbooks.git"

    user_data_script = f"""#!/bin/bash
    apt update -y
    apt install -y git python3-pip
    pip3 install ansible
    git clone {ansible_repo_url} /home/ubuntu/playbooks
    cd /home/ubuntu/playbooks
    ansible-playbook your-playbook.yml
    """

    user_data_script = f"""#!/bin/bash
        apt update -y
        apt install -y git python3-pip
        pip3 install ansible
        ansible-playbook your-playbook.yml
    """

    encoded_script = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

    subnet = os.environ["SUBNET_ID"]

    response = ec2.run_instances(
        ImageId="ami-0c02fb55956c7d316",  # Example: Ubuntu 20.04 LTS in us-east-1
        InstanceType="t2.micro",
        MinCount=1,
        MaxCount=1,
        # KeyName="your-keypair",  # Required for SSH
        # SecurityGroupIds=["sg-xxxxxxxx"],
        SubnetId=subnet,
        # IamInstanceProfile={'Name': 'your-ec2-role-with-s3-access'},
        UserData=encoded_script
    )

    instance_id = response["Instances"][0]["InstanceId"]

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "EC2 launched", "instance_id": instance_id})
    }
