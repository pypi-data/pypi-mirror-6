"""
GRIND runs jobs on EC2 spot instances
"""

import logging
import time
import sys
import os.path
import ConfigParser

import boto
import paramiko


FORMAT = "%(asctime)s %(levelname)8s %(funcName)-20s %(message)s"
WAIT = 60
KEY_FILENAME = os.path.join(os.path.expanduser('~'), '.grind.pem')


def main():
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger('paramiko').setLevel(logging.CRITICAL)
    logging.info('start')

    script = sys.argv[1]
    params = ' '.join(sys.argv[2:])
    logging.info('grinding %s %s', script, params)

    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(os.path.dirname(script),'grind.cfg')))

    try:
        before = config.get('ssh', 'before').strip().split('\n')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        before = []

    with SpotInstance(config.get('aws', 'instance_type'),
                      config.get('aws', 'product_description'),
                      config.get('aws', 'ami'),
                      config.get('aws', 'key_name'),
                      config.get('aws', 'security_group')) as spot:

        spot.run(script, params, before)

    logging.info('done')


class SpotInstance(object):
    """
    Context manager *trying* to instantiate an instance at the current spot price
    """

    def __init__(self, instance_type, product_description, ami, key_name, security_group):
        """
        Properties of the instance
        """
        self.instance_type = instance_type
        self.product_description = product_description
        self.ami = ami
        self.key_name = key_name
        self.security_group = security_group

    def __enter__(self):
        """
        Request an instance
        """
        self.ec2 = boto.connect_ec2()
        self.price = self.get_spot_price()
        self.instance = self.request_instance()
        return self

    def __exit__(self, type, value, traceback):
        """
        Terminate the instance
        """
        self.terminate()

    def get_spot_price(self):
        """
        Get spot price from EC2
        """
        logging.info('start')
        prices = self.ec2.get_spot_price_history(
            instance_type=self.instance_type,
            product_description=self.product_description)
        price = prices[0]
        logging.info('return: %s', price.price)
        return price

    def request_instance(self):
        """
        Request an instance at current spot price
        """
        logging.info('at %s', self.price.price)

        request = self.ec2.request_spot_instances(
            self.price.price,
            self.ami,
            key_name=self.key_name,
            security_groups=[self.security_group, ]).pop()

        while request.status.code != 'fulfilled' and \
              request.status.code != 'price-too-low':
            logging.info('request status %s', request.status.code)
            time.sleep(WAIT)
            request = self.ec2.get_all_spot_instance_requests(request_ids=[request.id,]).pop()

        if request.status.code == 'price-too-low':
            logging.info('request status %s', request.status.code)
            logging.info('done')
            return

        logging.info('instance %s', request.instance_id)
        reservation = self.ec2.get_all_reservations(instance_ids=[request.instance_id, ]).pop()
        instance = reservation.instances[0]
        self.ec2.create_tags([instance.id], {'Name': 'grind'})

        logging.info('%s state %s', instance.id, instance.state)
        while instance.state != 'running':
            time.sleep(WAIT)
            instance.update()
            logging.info('%s state %s', instance.id, instance.state)

        logging.info('return %s', instance.id)
        return instance

    def terminate(self):
        """
        Terminate the instance if it was ever started
        """

        if not self.instance:
            return

        logging.info('instance %s', self.instance.id)
        self.instance.terminate()
        logging.info('done')

    def run(self, script, params, before):
        """
        Run all the before commands (setup without creating an AMI) then upload
        script and run with params
        """
        if not self.instance:
            return

        logging.info('%s %s on %s', script, params, self.instance.id)

        time.sleep(WAIT) # giving the OS enough time to boot

        with SSH(self.instance.public_dns_name, KEY_FILENAME) as ssh:

            for command in before:
                ssh.execute('{0}'.format(command), swallow_return=True)

            uploaded = ssh.upload(script)

            ssh.execute('chmod u+x {0}'.format(uploaded), swallow_return=True)
            result = ssh.execute('./{0} {1}'.format(uploaded, params))

        logging.info('return %s', result)
        return result


class SSH(object):
    """
    Context manager handling SSH connection, command execution and SFTP upload
    """

    def __init__(self, public_dns_name, key_filename):
        """
        Host and key used for authentication
        """
        self.public_dns_name = public_dns_name
        self.key_filename = key_filename

    def __enter__(self):
        """
        Open SSH connection
        """
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """
        Close SSH connection
        """
        self.close()

    def open(self):
        """
        Instantiate and SSH connection to the EC2 instance
        """
        logging.info('ssh %s', self.public_dns_name)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.public_dns_name,
                         username='ubuntu',
                         key_filename=self.key_filename)
        logging.info('done')

    def close(self):
        """
        Close connection to the EC2 instance
        """
        logging.info('ssh to %s', self.public_dns_name)
        self.ssh.close()
        logging.info('done')

    def upload(self, filename):
        """
        Upload filename on the EC2 instance return the base name
        """
        logging.info('%s', filename)
        sftp = self.ssh.open_sftp()
        to = os.path.basename(filename)
        sftp.put(filename, to)
        sftp.close()
        logging.info('return %s', to)
        return to

    def execute(self, command, swallow_return=False):
        """
        Execute the command on the EC2 instance return sterr or stdout unless
        return is swallowed
        """
        logging.info('%s', command)
        stdin, stdout, stderr = self.ssh.exec_command(command)
        result = stdout.read().strip() or stderr.read().strip()
        if not swallow_return:
            logging.info('return %s', result)
            return result
        else:
            logging.info('done')


if __name__ == '__main__':
    main()
