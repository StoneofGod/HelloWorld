"""Generating CloudFormation template."""
from ipaddress import ip_network
from ipify import get_ip
from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)

ApplicationPort = "3000"
PublicCidrIp = str(ip_network(get_ip()))

t = Template()

t.set_description("Effective DevOps in AWS: HelloWorld web application")

keypair_param = t.add_parameter(
    Parameter(
        "KeyPair",
        Description="Name of an existing EC2 KeyPair to SSH",
        Type="AWS::EC2::KeyPair::KeyName",
        ConstraintDescription="must be the name of an existing EC2 KeyPair",
    )
)

security_group = t.add_resource(
    ec2.SecurityGroup(
        "SecurityGroup",
        GroupDescription=f"Allow SSH and TCP/{ApplicationPort} access",
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(
                IpProtocol="tcp", FromPort="22", ToPort="22", CidrIp=PublicCidrIp
            ),
            ec2.SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=int(ApplicationPort),
                ToPort=int(ApplicationPort),
                CidrIp=PublicCidrIp,
            ),
        ],
    )
)

user_data = Base64(
    Join(
        "\n",
        [
            "#!/bin/bash",
            "sudo yum install --enablerepo=epel -y nodejs",
            "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
            "wget http://bit.ly/2vVvT18 -O /etc/init/helloworld.conf",
            "start helloworld",
        ],
    )
)

ec2_instance = t.add_resource(
    ec2.Instance(
        "Instance",
        ImageId="ami-0b0ea68c435eb488d",  # Remplacer par une AMI valide si nécessaire
        InstanceType="t2.micro",
        SecurityGroups=[Ref(security_group)],  # Utilisé ici sans VPC context
        KeyName=Ref(keypair_param),
        UserData=user_data,
    )
)

t.add_output(
    Output(
        "WebUrl",
        Description="Application endpoint",
        Value=Join(
            "",
            [
                "http://",
                GetAtt("Instance", "PublicDnsName"),
                ":",
                ApplicationPort,
            ],
        ),
    )
)

print(t.to_json())


