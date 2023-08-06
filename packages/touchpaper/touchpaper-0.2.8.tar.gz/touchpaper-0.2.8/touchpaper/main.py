'''
This is the primary touchpaper module; the `main` function is called when you
run `touchpaper` on the command line.
'''

import sys

from colorama import init, Fore
from os import environ

from ._version import get_version
from .config import get_config
from .instance import Instance
from .prompts import *
from .utils import get_argument_parser, choice_prompt


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
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.version:
        print "touchpaper v%s" % get_version()
        sys.exit(0)

    ''' Retrieve and check config object and warn if env vars aren't set '''
    global config
    config.load(location_override=args.config_file_location)

    if config.data is False and \
        (config.AWS_KEY_ENV_VAR not in environ or config.AWS_SECRET_ENV_VAR not in environ):
        print Fore.RED + "Error: you're not using %s, so you need to configure the %s and %s variables in your environment." % (config.RC_FILE_NAME, config.AWS_KEY_ENV_VAR, config.AWS_SECRET_ENV_VAR)
        sys.exit(1)

    ''' Instantiate instance '''
    instance = Instance(dry_run=args.dry_run)

    pipeline = [
        prompt_for_credentials,
        prompt_for_region,
        prompt_for_availability_zone,
        prompt_for_ami,
        prompt_for_instance_type,
        prompt_for_atp,
        prompt_for_storage,
        prompt_for_storage_name,
        prompt_for_keypair,
        prompt_for_security_group,
        prompt_for_tags
    ]

    ''' Run the prompts pipeline to set up the instance parameters '''
    for pipeline_function in pipeline:
        pipeline_function(instance)

    ''' Regurgitate selected parameters for user confirmation '''
    instance.show_properties()

    if not bool(choice_prompt(['No', 'Yes'], 'Are these details correct?')):
        print Fore.YELLOW + "Quitting"
        sys.exit(0)

    print Fore.CYAN + "Launching instance..."
    instance.run()

    ''' That's it! '''
    print "Done."


if __name__ == '__main__':
    main()
