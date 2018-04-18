# aws configure --profile shotty
# s3 = boto3.resource('s3') 

import boto3

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

for i in ec2.instances.all():
    print(i)