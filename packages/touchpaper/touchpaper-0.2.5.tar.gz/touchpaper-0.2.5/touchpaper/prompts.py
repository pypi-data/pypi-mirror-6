from .utils import (choice_prompt,
                    get_instance_types,
                    text_prompt)


def prompt_for_ami(config):
    '''
    Read the list of favourite AMIs from config, if present, and prompt the
    user for a choice.

    They can also enter free text which is treated as an AMI ID.
    '''
    if config and 'favourite_amis' in config and config['favourite_amis']:
        favourite_amis = ["%s: %s" % (k, v) for k, v in config['favourite_amis'].iteritems()]
        selection = choice_prompt(favourite_amis, 'Please select an AMI or enter an AMI ID:', no_cast=True)
        if isinstance(selection, int):
            return favourite_amis[selection].split(':')[0]
        else:
            return selection
    else:
        return text_prompt('Please enter an AMI ID:')


def prompt_for_atp():
    '''
    Simple yes/no prompt for enabling Accidental Termination Protection
    '''
    return bool(choice_prompt(['No', 'Yes'], 'Do you want to enable Accidental Termination Protection?'))


def prompt_for_availability_zone(conn):
    '''
    Get a list of availability zones from the active connection/region and
    prompt the user
    '''
    available_zones = conn.get_all_zones()
    return available_zones[choice_prompt([x.name for x in available_zones], 'Please select a target availability zone:')]


def prompt_for_credentials(config):
    '''
    Prompt the user to choose from AWS credentials from the config

    FIXME: catch missing field in config file
    '''
    selection = choice_prompt([x['name'] for x in config['aws_credentials']], 'Please select a set of AWS credentials:')
    return (config['aws_credentials'][selection]['key'], config['aws_credentials'][selection]['secret'])


def prompt_for_instance_type():
    '''
    Prompt the user to choose from the local list of available instance types
    '''
    instance_types = get_instance_types()
    return instance_types[choice_prompt(instance_types, 'Please select an instance type:')]


def prompt_for_keypair(conn):
    '''
    Get a list of all keypairs from the current connection and prompt for
    which to use
    '''
    available_keypairs = conn.get_all_key_pairs()
    if not available_keypairs:
        return False
    return available_keypairs[choice_prompt([x.name for x in available_keypairs], 'Please select a keypair:')]


def prompt_for_region(conn):
    '''
    Get a list of available regions from the current connection and prompt
    the user for a choice
    '''
    available_regions = conn.get_all_regions()
    return available_regions[choice_prompt([x.name for x in available_regions], 'Please select a target region:')]


def prompt_for_security_group(conn):
    '''
    Get a list of available security groups from the current connection and
    prompt the user to choose one

    TODO: option to create new security group with sensible defaults
    '''
    available_security_groups = conn.get_all_security_groups()
    if not available_security_groups:
        return False
    return available_security_groups[choice_prompt([x.name for x in available_security_groups], 'Please select a security group:')]


def prompt_for_storage():
    '''
    Prompt the user to enter a size for a new EBS volume.

    If they enter 0 or nothing, return False, which skips volume creation.
    '''
    print "If you want to create and attach an EBS volume to this instance, enter its size in GB."
    print "Type 0 or press Enter to skip volume creation."
    size = text_prompt('Size of volume in GB:')
    if size == '' or int(size) == 0:
        return False
    return int(size)


def prompt_for_storage_name():
    '''
    Prompt the user to name the EBS volume they're creating
    '''
    name = text_prompt('Enter friendly name for volume:')
    return name or False


def prompt_for_tags(config):
    '''
    Prompt the user to enter tags for the instance, as specified in the config
    '''
    tags = {}
    for tag in config['tags']:
        name = tag['name']
        value = text_prompt('Enter value for tag "%s":' % name)
        tags[name] = value
    return tags
