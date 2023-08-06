import argparse


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

    FIXME: catch selection of invalid choice
    '''
    print prompt
    for i, choice in enumerate(choices):
        print " %d ) %s" % (i, choice)

    if kwargs.get('default') is not None:
        selection = raw_input("Enter your choice [%s]: " % kwargs['default'])
        if selection == '':
            selection = kwargs['default']
    else:
        selection = raw_input("Enter your choice: ")

    if kwargs.get('no_cast', False):
        return selection
    return int(selection)


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


def text_prompt(prompt, **kwargs):
    '''
    Show the user a text prompt and return their response

    TODO: 'default' input implementation
    '''
    selection = raw_input('%s ' % prompt)
    return selection
