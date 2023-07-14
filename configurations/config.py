import os
import configparser

class Config:
    def __init__(self):
        self.bucket = ''
        self.aws_access_key_id = ''
        self.aws_secret_access_key = ''
        self.region = 'ru-central1'
        self.endpoint_url = 'https://storage.yandexcloud.net'

    def load(self):
        config_file = os.path.expanduser('~/.config/cloudphoto/cloudphotorc')
        if not os.path.isfile(config_file):
            raise FileNotFoundError("Configuration file not found.")

        parser = configparser.ConfigParser()
        parser.read(config_file)

        default_section = parser['DEFAULT']
        self.bucket = default_section.get('bucket', '')
        self.aws_access_key_id = default_section.get('aws_access_key_id', '')
        self.aws_secret_access_key = default_section.get('aws_secret_access_key', '')

    def save(self):
        config_dir = os.path.expanduser('~/.config/cloudphoto')
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, 'cloudphotorc')
        parser = configparser.ConfigParser()
        parser['DEFAULT'] = {
            'bucket': self.bucket,
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key,
            'region': self.region,
            'endpoint_url': self.endpoint_url
        }

        with open(config_file, 'w') as file:
            parser.write(file)
