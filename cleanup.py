# aws configure --profile shotty
# s3 = boto3.resource('s3') 

import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

# Filter by tag

def filter_instances(project):
    instances = []

    if project:
        #!tag name and value are case sensitive!
        filters = [{'Name':'tag:Project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    
    return instances

#####################################
# Global group
#####################################

@click.group()
def cli():
    """Shotty manages snapshot"""

#####################################
# Snapshot group
#####################################

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

# Snapshot command list

@snapshots.command('list')
@click.option('--project', default=None,
    help="only snapshots for project (tag project:<name>)")
def list_snapshots(project):
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all(): 
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.start_time.strftime("%c")
            )))

#last snapshot only:            if s.state == 'completed': break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="only volumes for project (tag project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

#####################################
# Instances group
#####################################

@cli.group('instances')
def instances():
    """Commands for instances"""

# Instances command snapshot

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="only instances for project (tag project:<name>)")
def create_snapshots(project):
    "Create snapshots"

    instances = filter_instances(project)

    for i in instances:
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by snapscript") 

        print("starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's done")

    return

# Instances command list

@instances.command('list')
@click.option('--project', default=None,
    help="only instances for project (tag project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project','<no projet>')
            )))

    return

# Instances command stop

@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project')
def stop_instance(project):
    "stop EC2 instances"

    instances = filter_instances(project)   

    for i in instances:
        print("stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

# Instances command start

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project')
def start_instance(project):
    "start EC2 instances"

    instances = filter_instances(project)   

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}. ".format(i.id) + str(e))
            continue
    return

#####################################
# Script execution
#####################################

if __name__ == '__main__':
    cli()