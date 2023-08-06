import boto.ec2

from colorama import Fore
from time import sleep

from .config import get_config


config = get_config()


class Instance:
    region = None
    availability_zone = None
    ami = None
    instance_type = None
    atp = False
    storage_name = None
    storage_size = 0
    keypair = None
    security_group = None
    tags = {}

    key = None
    secret = None
    conn = None

    _dry_run = False
    _instance = None
    _bdm = None

    def __init__(self, **kwargs):
        ''' Pick up dry-run arg if set '''
        self._dry_run = kwargs.get('dry_run', False)

        if self._dry_run:
            print Fore.YELLOW + "Warning: dry-run mode is active"

    def prep_storage(self):
        '''
        If a storage size is specified, set up the EC2 BlockDeviceMapping ready
        to attach it to the instance at launch
        (source: http://stackoverflow.com/a/13604274/258794)
        '''
        if self.storage_size != 0:
            dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
            dev_sda1.size = self.storage_size
            bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
            bdm['/dev/sda1'] = dev_sda1
            self._bdm = bdm
        return self

    def run(self):
        ''' Initiate the instance with boto's run_instances() '''
        if self.conn:
            res = self.conn.run_instances(image_id=self.ami,
                                          key_name=self.keypair.name if self.keypair else None,
                                          security_groups=[self.security_group.name,],
                                          instance_type=self.instance_type,
                                          placement=self.availability_zone.name,
                                          block_device_map=self._bdm if self._bdm else None,
                                          disable_api_termination=self.atp,
                                          dry_run=self._dry_run)
            self._instance = res.instances[0]

            ''' Wait until the instance reports a running state '''
            while self._instance.state != config.RUNNING_STATE:
                print "Instance state: %s ..." % self._instance.state
                sleep(5)
                self._instance.update()
            print Fore.GREEN + "Instance running! ID: %s; public DNS: %s" % (self._instance.id, self._instance.public_dns_name)

            ''' If any tags were entered, add them to the instance now '''
            if self.tags:
                self.set_tags()
                print "Instance tags added"

            ''' If storage was selected and given a name, apply it to the volume '''
            if self.storage_name:
                self.set_storage_tag()
        return self

    def set_storage_tag(self):
        ''' Tag the instance's storage with a name '''
        if self._instance and self.storage_name:
            volumes = self.conn.get_all_volumes(filters={ 'attachment.instance-id': self._instance.id })
            if volumes:
                volumes[0].add_tag('Name', self.storage_name)
                print "EBS volume tags added"
        return self

    def set_tags(self):
        ''' Tag the instance '''
        if self.tags:
            for tag, value in self.tags.iteritems():
                self._instance.add_tag(tag, value)
        print "Instance tags added"
        return self

    def show_properties(self):
        ''' Print instance properties for user confirmation '''
        print Fore.GREEN + "\nReady to launch instance. You selected the following:"
        print "Region: %s" % self.region.name
        print "Availability zone: %s" % self.availability_zone.name
        print "AMI: %s" % self.ami
        print "Instance type: %s" % self.instance_type
        print "Accidental termination protection: %s" % ("Yes" if self.atp else "No")
        print "Storage: %s" % (('%dGB EBS' % self.storage_size) if self.storage_size else "None")
        print "Keypair: %s" % (self.keypair.name if self.keypair else "None")
        print "Security group: %s" % self.security_group.name

        if self.tags:
            print "Tags:"
            for tag, value in self.tags.iteritems():
                print '- "%s": "%s"' % (tag, value)
