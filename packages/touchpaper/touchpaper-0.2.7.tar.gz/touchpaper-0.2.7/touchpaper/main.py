'''
This is the primary touchpaper module; the `main` function is called when you
run `touchpaper` on the command line.
'''

import boto.ec2
import sys

from boto.ec2 import EC2Connection
from colorama import init, Fore
from os import environ
from time import sleep

from ._version import get_version
from .config import get_config
from .prompts import *
from .utils import argument_parser, choice_prompt


config = get_config()


'''
Main package routine

Pulls it all together. Initiates various prompts to the user to build an EC2
API query to launch an instance.
'''
def main():
    ''' Colorama init '''
    init(autoreset=True)

    ''' Argument parser init '''
    parser = argument_parser()
    args = parser.parse_args()

    if args.version:
        print "touchpaper v%s" % get_version()
        sys.exit(0)

    if args.dry_run:
        print Fore.YELLOW + "Warning: dry-run mode is active"

    ''' Retrieve and check config object and warn if env vars aren't set '''
    global config
    config.load(location_override=args.config_file_location)
    if config.data is False and (config.AWS_KEY_ENV_VAR not in environ or config.AWS_SECRET_ENV_VAR not in environ):
        print Fore.RED + "Error: you're not using %s, so you need to configure the %s and %s variables in your environment." % (config.RC_FILE_NAME, config.AWS_KEY_ENV_VAR, config.AWS_SECRET_ENV_VAR)
        sys.exit(1)

    ''' Set up initial EC2 connection '''
    if config.data:
        key, secret = prompt_for_credentials()
        conn = EC2Connection(key, secret)
    else:
        print Fore.YELLOW + "Using AWS credentials from environment"
        conn = EC2Connection()

    region = prompt_for_region(conn)

    ''' Establish region using selected credentials, or default to environment
    variables '''
    if config.data:
        conn = boto.ec2.connect_to_region(region.name, aws_access_key_id=key, aws_secret_access_key=secret)
    else:
        conn = boto.ec2.connect_to_region(region.name)

    availability_zone = prompt_for_availability_zone(conn)

    ami = prompt_for_ami()

    instance_type = prompt_for_instance_type()

    atp = prompt_for_atp()

    storage = prompt_for_storage()
    storage_name = False
    if storage:
        '''
        If a storage size was specified, prompt for the name to assign to the
        volume and set up the EC2 BlockDeviceMapping ready to attach it to the
        instance at launch (source: http://stackoverflow.com/a/13604274/258794)
        '''
        storage_name = prompt_for_storage_name()

        dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
        dev_sda1.size = storage
        bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        bdm['/dev/sda1'] = dev_sda1

    keypair = prompt_for_keypair(conn)
    if keypair is False:
        print Fore.RED + "Warning: no keypairs found on account, you will not be able to SSH into the new instance"

    security_group = prompt_for_security_group(conn)
    if security_group is False:
        print Fore.RED + "Warning: no security groups found on account, you will not be able to access the new instance via the network"

    if config.data and 'tags' in config.data:
        tags = prompt_for_tags()
    else:
        tags = None
        print Fore.YELLOW + "Warning: no tags defined in config"

    ''' Regurgitate selected parameters for user confirmation '''
    print Fore.GREEN + "\nReady to launch instance. You selected the following:"
    print "Region: %s" % region.name
    print "Availability zone: %s" % availability_zone.name
    print "AMI: %s" % ami
    print "Instance type: %s" % instance_type
    print "Accidental termination protection: %s" % ("Yes" if atp else "No")
    print "Storage: %s" % (('%dGB EBS' % storage) if storage else "None")
    print "Keypair: %s" % (keypair.name if keypair else "None")
    print "Security group: %s" % security_group.name
    if tags:
        print "Tags:"
        for tag, value in tags.iteritems():
            print '- "%s": "%s"' % (tag, value)

    if not bool(choice_prompt(['No', 'Yes'], 'Are these details correct?')):
        print Fore.YELLOW + "Quitting"
        sys.exit(0)

    print Fore.CYAN + "Launching instance..."

    ''' Request a reservation with the selected parameters '''
    reservation = conn.run_instances(image_id=ami,
                                     key_name=keypair.name if keypair else None,
                                     security_groups=[security_group.name,],
                                     instance_type=instance_type,
                                     placement=availability_zone.name,
                                     block_device_map=bdm if storage else None,
                                     disable_api_termination=atp,
                                     dry_run=args.dry_run)
    instance = reservation.instances[0]

    ''' Wait until the instance reports a running state '''
    while instance.state != config.RUNNING_STATE:
        print "Instance state: %s ..." % instance.state
        sleep(5)
        instance.update()
    print Fore.GREEN + "Instance running! ID: %s; public DNS: %s" % (instance.id, instance.public_dns_name)

    ''' If any tags were entered, add them to the instance now '''
    if tags:
        for tag, value in tags.iteritems():
            instance.add_tag(tag, value)
        print "Instance tags added"

    ''' If storage was selected and given a name, apply it to the volume '''
    if storage_name:
        volumes = conn.get_all_volumes(filters={ 'attachment.instance-id': instance.id })
        if volumes:
            volumes[0].add_tag('Name', storage_name)
            print "EBS volume tags added"

    ''' That's it! '''
    print "Done."


if __name__ == '__main__':
    main()
