import sys
import argparse

from configurations.config import Config
from program.Storage import Storage


def main():
    parser = argparse.ArgumentParser(prog='cloudphoto', description='Yandex Object Storage Photo Album Site Generator')
    parser.add_argument('command', choices=['list', 'upload', 'delete', 'mksite', 'init'], help='command to execute')
    parser.add_argument('--album', help='name of the album')
    parser.add_argument('--path', help='absolute or relative path to the photo directory')
    args = parser.parse_args()

    config = Config()
    config.load()

    if args.command != 'init':
        if not config.bucket or not config.aws_access_key_id or not config.aws_secret_access_key:
            print("Error: Incomplete configuration. Run 'cloudphoto init' to initialize the program.")
            sys.exit(1)

    storage = Storage(config)
    storage.connect()

    if args.command == 'list':
        albums = storage.list_albums()
        if albums:
            for album in albums:
                print(album)
        else:
            print("Photo albums not found")

    elif args.command == 'upload':
        if not args.album:
            print("Error: The --album option is required for the 'upload' command.")
            sys.exit(1)

        album_name = args.album
        photos_dir = args.path or '.'
        try:
            storage.upload_photos(album_name, photos_dir)
        except ValueError as e:
            print(str(e))
            sys.exit(1)

    elif args.command == 'delete':
        if not args.album:
            print("Error: The --album option is required for the 'delete' command.")
            sys.exit(1)

        album_name = args.album
        storage.delete_album(album_name)

    elif args.command == 'mksite':
        albums = storage.list_albums()
        if albums:
            for album in albums:
                storage.generate_album_page(album.name)
            storage.generate_index_page(albums)
            storage.generate_error_page()
            storage.publish_website()
            print(f"Website published at https://{config.bucket}.website.yandexcloud.net/")
        else:
            print("Photo albums not found")

    elif args.command == 'init':
        config.bucket = input("Enter the bucket name: ")
        config.aws_access_key_id = input("Enter the AWS access key ID: ")
        config.aws_secret_access_key = input("Enter the AWS secret access key: ")
        config.save()
        print("Initialization successful.")

if __name__ == '__main__':
    main()
