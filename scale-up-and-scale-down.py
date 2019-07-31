import boto3
import pickle


class Scaleup:
    def __init__(self, conf):
        self.conf = conf
        pass

    # creates ec2
    def create_ec2(self):
        ec2 = boto3.resource("ec2")
        instance = ec2.create_instances(
            ImageId=self.conf["ami"],
            MinCount=1,
            MaxCount=1,
            InstanceType=self.conf["instance_size"],
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {"VolumeSize": self.conf["VolumeSize"]},
                }
            ],
            KeyName=self.conf["ssh_key"],
            SecurityGroupIds=[self.conf["sec"]],
        )
        host = instance[0]
        print(host.id)
        ec2.create_tags(
            Resources=[host.id],
            Tags=[{"Key": "Name", "Value": "scale_" + self.conf["tag"] + ""}],
        )
        host = ec2.Instance(host.id)
        ec2 = boto3.client("ec2")
        self.attach(host.id)
        return host

    # attach to load balancer
    def attach(self, id):
        client = boto3.client("elb")
        response = client.register_instances_with_load_balancer(
            LoadBalancerName=self.conf["loadbalancer"], Instances=[{"InstanceId": id}]
        )

    # get ec2 by name tells max instance
    def get_by_name(self):
        ec2 = boto3.client("ec2")
        filters = [
            {"Name": "tag:Name", "Values": ["scale_" + self.conf["tag"]]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
        reservations = ec2.describe_instances(Filters=filters)
        # print(reservations['Reservations'][0]['Instances'])
        if len(reservations["Reservations"]) >= 2:
            return False
        else:
            return True

    # get if dev is running
    def dev_running(self):
        ec2 = boto3.client("ec2")
        filters = [
            {"Name": "tag:Name", "Values": ["dev_" + self.conf["tag"] + ""]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
        reservations = ec2.describe_instances(Filters=filters)
        if len(reservations["Reservations"]) >= 1:
            return False
        else:
            return True


class Scaledown:
    def __init__(self, conf):
        self.conf = conf

    # detache from loadbalancer
    def detache(self, id):
        client = boto3.client("elb")
        response = client.deregister_instances_from_load_balancer(
            LoadBalancerName=self.conf["loadbalancer"], Instances=[{"InstanceId": id}]
        )

    # get all instances by name
    def get_by_name(self):
        ec2 = boto3.client("ec2")
        filters = [
            {"Name": "tag:Name", "Values": ["scale_" + self.conf["tag"] + ""]},
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
        ]
        reservations = ec2.describe_instances(Filters=filters)
        # print(reservations['Reservations'][0]['Instances'])
        if len(reservations["Reservations"]) >= 1:
            print(reservations["Reservations"])
            for i in reservations["Reservations"]:
                print(i["Instances"][0]["InstanceId"])
                self.detache(i["Instances"][0]["InstanceId"])
                self.delete(i["Instances"][0]["InstanceId"])

    # Treminate
    def delete(self, id):
        ec2 = boto3.client("ec2")
        ec2.terminate_instances(InstanceIds=[id])


def lambda_handler(event, context):

    if "testing_scale" in event["ami"]["Records"][0]["Sns"]["Subject"]:
        conf = download_old_ami("test_scale")
        create = Scaleup(conf)

        if create.dev_running():
            if create.get_by_name():
                create.create_ec2()

    elif "testing_down" in event["ami"]["Records"][0]["Sns"]["Subject"]:
        conf = download_old_ami("testing_scale")
        destroy = Scaledown(conf)
        destroy.get_by_name()


def download_old_ami(key):
    sclient = boto3.client("s3")
    response = sclient.get_object(Bucket="testing", Key=key)
    body_string = response["Body"].read()
    positive_model_data = pickle.loads(body_string)
    print(positive_model_data)
    return positive_model_data
