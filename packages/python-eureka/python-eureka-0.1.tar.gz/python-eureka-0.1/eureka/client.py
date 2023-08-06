import json
from urlparse import urljoin
from eureka import requests
import ec2metadata


class EurekaClient(object):
    def __init__(self, app_name, eureka_url=None, host_name=None, data_center="Amazon"):
        super(EurekaClient, self).__init__()
        self.app_name = app_name
        self.eureka_url = eureka_url
        self.host_name = host_name
        if not data_center == "Amazon":
            assert self.host_name, "Please provide a hostname, when not using Amazon."
        self.data_center = data_center

    def register(self, initial_status="STARTING"):
        data_center_info = {
            'name': self.data_center
        }
        if self.data_center == "Amazon":
            data_center_info['metadata'] = {
                'ami-launch-index': ec2metadata.get('ami-launch-index'),
                'local-hostname': ec2metadata.get('local-hostname'),
                'availability-zone': ec2metadata.get('availability-zone'),
                'instance-id': ec2metadata.get('instance-id'),
                'public-ipv4': ec2metadata.get('public-ipv4'),
                'public-hostname': ec2metadata.get('public-hostname'),
                'ami-manifest-path': ec2metadata.get('ami-manifest-path'),
                'local-ipv4': ec2metadata.get('local-ipv4'),
                'ami-id': ec2metadata.get('ami-id'),
                'instance-type': ec2metadata.get('instance-type'),
            }
        r = requests.post(urljoin(self.eureka_url, "apps/%s" % self.app_name), json.dumps({
            'instance': {
                'hostName': self.host_name,
                'app': self.app_name,
                'vipAddr': '127.0.0.1',
                'secureVipAddr': '127.0.0.1',
                'status': initial_status,
                'port': '5000',
                'securePort': '443',
                'dataCenterInfo': data_center_info
            }
        }), headers={'Content-Type': 'application/json'})
        r.raise_for_status()

    def update_status(self, new_status):
        r = requests.put(urljoin(self.eureka_url, "apps/%s/%s/status?value=%s" % (
            self.app_name,
            self.host_name,
            new_status
        )))
        r.raise_for_status()

    def heartbeat(self):
        r = requests.put(urljoin(self.eureka_url, "apps/%s/%s" % (self.app_name, self.host_name)))
        r.raise_for_status()