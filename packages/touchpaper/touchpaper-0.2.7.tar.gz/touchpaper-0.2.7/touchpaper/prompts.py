from .config import get_config
from .utils import (choice_prompt,
                    get_instance_types,
                    text_prompt)


config = get_config()


def prompt_for_ami():
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
            return favourite_amis[selection].split(':')[0]
        else:
            # selection is a string, hopefully an AMI ID
            if selection == '':
                raise ValueError("No selection or AMI ID specified")
            return selection
    else:
        return text_prompt('Please enter an AMI ID:')


def prompt_for_atp():
    '''
    Simple yes/no prompt for enabling Accidental Termination Protection
    '''
    selection = choice_prompt(['No', 'Yes'],
                              'Do you want to enable Accidental Termination Protection?',
                              default=config.get_default('atp'))
    config.set_default('atp', selection)
    return bool(selection)


def prompt_for_availability_zone(conn):
    '''
    Get a list of availability zones from the active connection/region and
    prompt the user
    '''
    available_zones = conn.get_all_zones()
    selection = choice_prompt([x.name for x in available_zones],
                              'Please select a target availability zone:',
                              default=config.get_default('availability_zone'))
    config.set_default('availability_zone', selection)
    return available_zones[selection]


def prompt_for_credentials():
    '''
    Prompt the user to choose from AWS credentials from the config

    FIXME: catch missing field in config file
    '''
    choices = [x['name'] for x in config.data['aws_credentials']]
    selection = choice_prompt(choices,
                              'Please select a set of AWS credentials:',
                              default=config.get_default('credentials'))
    config.set_default('credentials', selection)
    return (config.data['aws_credentials'][selection]['key'],
            config.data['aws_credentials'][selection]['secret'])


def prompt_for_instance_type():
    '''
    Prompt the user to choose from the local list of available instance types
    '''
    instance_types = get_instance_types()
    selection = choice_prompt(instance_types,
                              'Please select an instance type:',
                              default=config.get_default('instance_type'))
    config.set_default('instance_type', selection)
    return instance_types[selection]


def prompt_for_keypair(conn):
    '''
    Get a list of all keypairs from the current connection and prompt for
    which to use
    '''
    available_keypairs = conn.get_all_key_pairs()
    if not available_keypairs:
        return False
    selection = choice_prompt([x.name for x in available_keypairs],
                              'Please select a keypair:',
                              default=config.get_default('keypair'))
    config.set_default('keypair', selection)
    return available_keypairs[selection]


def prompt_for_region(conn):
    '''
    Get a list of available regions from the current connection and prompt
    the user for a choice
    '''
    available_regions = conn.get_all_regions()
    selection = choice_prompt([x.name for x in available_regions],
                              'Please select a target region:',
                              default=config.get_default('region'))
    config.set_default('region', selection)
    return available_regions[selection]


def prompt_for_security_group(conn):
    '''
    Get a list of available security groups from the current connection and
    prompt the user to choose one

    TODO: option to create new security group with sensible defaults
    '''
    available_security_groups = conn.get_all_security_groups()
    if not available_security_groups:
        return False
    selection = choice_prompt([x.name for x in available_security_groups],
                              'Please select a security group:',
                              default=config.get_default('security_group'))
    config.set_default('security_group', selection)
    return available_security_groups[selection]


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


def prompt_for_tags():
    '''
    Prompt the user to enter tags for the instance, as specified in the config
    '''
    tags = {}
    for tag in config.data['tags']:
        name = tag['name']
        value = text_prompt('Enter value for tag "%s":' % name)
        tags[name] = value
    return tags
