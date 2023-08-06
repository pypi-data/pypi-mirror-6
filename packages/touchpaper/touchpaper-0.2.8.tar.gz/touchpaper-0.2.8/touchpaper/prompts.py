import boto.ec2

from boto.ec2 import EC2Connection
from colorama import Fore

from .config import get_config
from .utils import (choice_prompt,
                    get_instance_types,
                    text_prompt)


config = get_config()


def prompt_for_ami(instance):
    '''
    Read the list of favourite AMIs from config, if present, and prompt the
    user for a choice.

    They can also enter free text which is treated as an AMI ID.
    '''
    if config.data and config.data.get('favourite_amis', False):
        favourite_amis = ["%s: %s" % (k, v) for k, v in config.data['favourite_amis'].iteritems()]
        selection = choice_prompt(favourite_amis,
                                  'Please select an AMI or enter an AMI ID:',
                                  no_cast=True,
                                  default=config.get_default('ami'))
        if isinstance(selection, int) or selection.isdigit():
            selection = int(selection)
            config.set_default('ami', selection)
            instance.ami = favourite_amis[selection].split(':')[0]
        else:
            # selection is a string, hopefully an AMI ID
            if selection == '':
                raise ValueError("No selection or AMI ID specified")
            instance.ami = selection
    else:
        instance.ami = text_prompt('Please enter an AMI ID:')

    return instance


def prompt_for_atp(instance):
    '''
    Simple yes/no prompt for enabling Accidental Termination Protection
    '''
    selection = choice_prompt(['No', 'Yes'],
                              'Do you want to enable Accidental Termination Protection?',
                              default=config.get_default('atp'))
    config.set_default('atp', selection)
    instance.atp = bool(selection)

    return instance


def prompt_for_availability_zone(instance):
    '''
    Get a list of availability zones from the active connection/region and
    prompt the user
    '''
    available_zones = instance.conn.get_all_zones()
    selection = choice_prompt([x.name for x in available_zones],
                              'Please select a target availability zone:',
                              default=config.get_default('availability_zone'))
    config.set_default('availability_zone', selection)
    instance.availability_zone = available_zones[selection]

    return instance


def prompt_for_credentials(instance):
    '''
    Prompt the user to choose from AWS credentials from the config or
    environment, then set up initial EC2 connection
    '''

    if config.data and 'aws_credentials' in config.data:
        choices = [x['name'] for x in config.data['aws_credentials']]
        selection = choice_prompt(choices,
                                  'Please select a set of AWS credentials:',
                                  default=config.get_default('credentials'))
        config.set_default('credentials', selection)

        instance.key = config.data['aws_credentials'][selection]['key']
        instance.secret = config.data['aws_credentials'][selection]['secret']
        instance.conn = EC2Connection(instance.key, instance.secret)
    else:
        print Fore.YELLOW + "Using AWS credentials from environment"
        instance.conn = EC2Connection()

    return instance


def prompt_for_instance_type(instance):
    '''
    Prompt the user to choose from the local list of available instance types
    '''
    instance_types = get_instance_types()
    selection = choice_prompt(instance_types,
                              'Please select an instance type:',
                              default=config.get_default('instance_type'))
    config.set_default('instance_type', selection)
    instance.instance_type = instance_types[selection]

    return instance


def prompt_for_keypair(instance):
    '''
    Get a list of all keypairs from the current connection and prompt for
    which to use
    '''
    available_keypairs = instance.conn.get_all_key_pairs()
    if available_keypairs:
        selection = choice_prompt([x.name for x in available_keypairs],
                                  'Please select a keypair:',
                                  default=config.get_default('keypair'))
        config.set_default('keypair', selection)
        instance.keypair = available_keypairs[selection]

    if instance.keypair is None:
        print Fore.RED + "Warning: no keypairs found on account, you will not be able to SSH into the new instance"

    return instance


def prompt_for_region(instance):
    '''
    Get a list of available regions from the current connection and prompt
    the user for a choice, then connect to the region
    '''
    available_regions = instance.conn.get_all_regions()
    selection = choice_prompt([x.name for x in available_regions],
                              'Please select a target region:',
                              default=config.get_default('region'))
    config.set_default('region', selection)
    instance.region = available_regions[selection]

    ''' Establish region using selected credentials, or default to environment
    variables '''
    if config.data:
        instance.conn = boto.ec2.connect_to_region(instance.region.name,
                                                   aws_access_key_id=instance.key,
                                                   aws_secret_access_key=instance.secret)
    else:
        instance.conn = boto.ec2.connect_to_region(instance.region.name)

    return instance


def prompt_for_security_group(instance):
    '''
    Get a list of available security groups from the current connection and
    prompt the user to choose one
    '''
    available_security_groups = instance.conn.get_all_security_groups()
    if available_security_groups:
        selection = choice_prompt([x.name for x in available_security_groups],
                                  'Please select a security group:',
                                  default=config.get_default('security_group'))
        config.set_default('security_group', selection)
        instance.security_group = available_security_groups[selection]

    if instance.security_group is None:
        print Fore.RED + "Warning: no security groups found on account, you will not be able to access the new instance via the network"

    return instance


def prompt_for_storage(instance):
    '''
    Prompt the user to enter a size for a new EBS volume.

    If they enter 0 or nothing skip volume creation.
    '''
    print "If you want to create and attach an EBS volume to this instance, enter its size in GB."
    print "Type 0 or press Enter to skip volume creation."
    size = text_prompt('Size of volume in GB:')
    if size == '' or int(size) == 0:
        return instance

    instance.storage_size = int(size)
    instance.prep_storage()

    return instance


def prompt_for_storage_name(instance):
    '''
    Prompt the user to name the EBS volume they're creating
    '''
    if instance.storage_size != 0:
        name = text_prompt('Enter friendly name for volume:')
        if name:
            instance.storage_name = name

    return instance


def prompt_for_tags(instance):
    '''
    Prompt the user to enter tags for the instance, as specified in the config
    '''
    if config.data and 'tags' in config.data:
        tags = {}
        for tag in config.data['tags']:
            name = tag['name']
            value = text_prompt('Enter value for tag "%s":' % name)
            tags[name] = value
        instance.tags = tags
    else:
        print Fore.YELLOW + "Warning: no tags defined in config"

    return instance
