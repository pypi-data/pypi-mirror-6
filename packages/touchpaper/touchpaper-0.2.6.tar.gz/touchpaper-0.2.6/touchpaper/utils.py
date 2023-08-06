import argparse
import json
import touchpaper.settings as settings

from os import getcwd
from os.path import exists, expanduser, join


def argument_parser():
    '''
    Parse command-line args for run-time options
    '''
    parser = argparse.ArgumentParser(description='Asks a series of questions '
                                                 'to configure and launch an '
                                                 'AWS EC2 instance')
    parser.add_argument('-c', '--config', dest='config_file_location',
                        action='store', help='override location of config file')
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='enable dry-run mode in the AWS API')
    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='show package version information and exit')
    return parser


def choice_prompt(choices, prompt, **kwargs):
    '''
    Present the user with some numbered choices and accept input to make a
    selection

    TODO: 'default' option implementation
    '''
    print prompt
    for i, choice in enumerate(choices):
        print " %d ) %s" % (i, choice)
    selection = raw_input("Enter your choice: ")

    if 'no_cast' in kwargs and kwargs['no_cast'] == True:
        return selection
    return int(selection)


def find_config(config_file_location_override):
    '''
    Search the current user's home directory, or the current directory, for
    our rc file. If found, attempt to parse it.
    '''
    local_config_path = join(getcwd(), settings.RC_FILE_NAME)
    home_config_path = join(expanduser('~'), settings.RC_FILE_NAME)
    config_path = False
    config = False

    if config_file_location_override:
        if exists(config_file_location_override):
            config_path = config_file_location_override
    else:
        if exists(local_config_path):
            config_path = local_config_path
        elif exists(home_config_path):
            config_path = home_config_path

    if config_path:
        with open(config_path) as f:
            config = json.load(f)
    return config


def get_instance_types():
    '''
    Hardcoded list of available instance types as described by the EC2 API
    '''
    return [
        "t1.micro",
        "m1.small",
        "m1.medium",
        "m1.large",
        "m1.xlarge",
        "m3.xlarge",
        "m3.2xlarge",
        "c1.medium",
        "c1.xlarge",
        "m2.xlarge",
        "m2.2xlarge",
        "m2.4xlarge",
        "cr1.8xlarge",
        "hi1.4xlarge",
        "hs1.8xlarge",
        "cc1.4xlarge",
        "cg1.4xlarge",
        "cc2.8xlarge",
        "g2.2xlarge",
        "c3.large",
        "c3.xlarge",
        "c3.2xlarge",
        "c3.4xlarge",
        "c3.8xlarge",
        "i2.xlarge",
        "i2.2xlarge",
        "i2.4xlarge",
        "i2.8xlarge",
    ]


def text_prompt(prompt, **args):
    '''
    Show the user a text prompt and return their response

    TODO: 'default' input implementation
    '''
    selection = raw_input('%s ' % prompt)
    return selection
