from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "InfrastructureQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        
        vpc = ec2.Vpc.from_lookup(
            self,
            "DefaultVpc",
            is_default = True
        )

        sg = ec2.SecurityGroup(
            self,
            "ServerSecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8080),
            "Allow protohackers traffic"
        )
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
            "Allow SSH",
        )

        instance = ec2.Instance(
            self,
            "Server",
            vpc=vpc,
            security_group=sg,
            key_pair=ec2.KeyPair.from_key_pair_name(
                self,
                "ServerKeyPair",
                "Caleb's ThinkPad",
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO,
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023()
        )

        instance.user_data.add_commands(
            "sudo dnf -y install python3.14"
        )
