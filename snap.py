# aws configure --profile shotty
# s3 = boto3.resource('s3') 

import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.command()
@click.option('--project', default=None,
    help="only instance for project (tag project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = []

    if project:
        #!tag name and value are case sensitive!
        filters = [{'Name':'tag:project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    for i in instances:
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name)))
    return

list_instances()