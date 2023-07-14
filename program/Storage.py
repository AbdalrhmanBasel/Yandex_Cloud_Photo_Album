import os
import boto3

from program.Album import Album


class Storage:
    def __init__(self, config):
        self.config = config
        self.s3_client = None

    def connect(self):
        self.s3_client = boto3.client(
            's3',
            region_name=self.config.region,
            endpoint_url=self.config.endpoint_url,
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key
        )

    def list_albums(self):
        response = self.s3_client.list_objects_v2(Bucket=self.config.bucket, Prefix='albums/', Delimiter='/')
        albums = [prefix['Prefix'][7:-1] for prefix in response.get('CommonPrefixes', [])]
        albums.sort()
        return [Album(name) for name in albums]

    def create_album(self, album_name):
        self.s3_client.put_object(Bucket=self.config.bucket, Key=f'albums/{album_name}/')

    def upload_photos(self, album_name, photos_dir):
        if not os.path.isdir(photos_dir):
            raise ValueError(f"No such directory '{photos_dir}'")

        photos = []
        for root, _, files in os.walk(photos_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    photos.append(os.path.join(root, file))

        if not photos:
            raise ValueError(f"No photos found in directory '{photos_dir}'")

        for photo in photos:
            photo_key = f'albums/{album_name}/{os.path.basename(photo)}'
            try:
                self.s3_client.upload_file(photo, self.config.bucket, photo_key)
            except Exception as e:
                print(f"Warning: Photo not sent {photo}")
                continue

    def delete_album(self, album_name):
        response = self.s3_client.list_objects_v2(Bucket=self.config.bucket, Prefix=f'albums/{album_name}/')
        photos = [{'Key': obj['Key']} for obj in response.get('Contents', [])]
        if photos:
            self.s3_client.delete_objects(Bucket=self.config.bucket, Delete={'Objects': photos})
        self.s3_client.delete_object(Bucket=self.config.bucket, Key=f'albums/{album_name}/')

    def generate_album_page(self, album_name):
        response = self.s3_client.list_objects_v2(Bucket=self.config.bucket, Prefix=f'albums/{album_name}/')
        photos = response.get('Contents', [])
        photo_html = ""
        for photo in photos:
            photo_url = self.s3_client.generate_presigned_url(
                'get_object', Params={'Bucket': self.config.bucket, 'Key': photo['Key']}
            )
            photo_html += f'<img src="{photo_url}" data-title="{os.path.basename(photo["Key"])}">\n'

        with open('album_template.html', 'r') as file:
            album_template = file.read()

        album_html = album_template.replace('{{photo_html}}', photo_html)
        self.s3_client.put_object(Bucket=self.config.bucket, Key=f'album{album_name}.html', Body=album_html)

    def generate_index_page(self, albums):
        album_links = ""
        for i, album in enumerate(albums, start=1):
            album_links += f'<li><a href="album{i}.html">{album}</a></li>\n'

        with open('index_template.html', 'r') as file:
            index_template = file.read()

        index_html = index_template.replace('{{album_links}}', album_links)
        self.s3_client.put_object(Bucket=self.config.bucket, Key='index.html', Body=index_html)

    def generate_error_page(self):
        with open('error_template.html', 'r') as file:
            error_template = file.read()

        self.s3_client.put_object(Bucket=self.config.bucket, Key='error.html', Body=error_template)

    def publish_website(self):
        self.s3_client.put_bucket_website(
            Bucket=self.config.bucket,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'error.html'}
            }
        )
