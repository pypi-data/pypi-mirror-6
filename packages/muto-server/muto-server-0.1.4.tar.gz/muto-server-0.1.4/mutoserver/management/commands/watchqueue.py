from io import BytesIO
import json
import os

import boto
from boto.s3.key import Key
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.db.models.loading import get_model
from easy_thumbnails.files import get_thumbnailer
import redis
import requests


class Command(NoArgsCommand):
    help = 'Watch queue and generate image versions'

    def handle_noargs(self, **options):
        self.redis = redis.StrictRedis.from_url(getattr(settings, 'MUTO_REDIS_URL', 'redis://:6379'))
        self.s3 = boto.connect_s3(aws_access_key_id=getattr(settings, 'MUTO_AWS_ACCESS_KEY_ID', getattr(settings, 'AWS_ACCESS_KEY_ID', os.getenv('AWS_ACCESS_KEY_ID'))), aws_secret_access_key=getattr(settings, 'MUTO_AWS_SECRET_ACCESS_KEY', getattr(settings, 'AWS_SECRET_ACCESS_KEY', os.getenv('AWS_SECRET_ACCESS_KEY'))))

        pubsub = self.redis.pubsub()
        pubsub.subscribe('muto:queue')

        self.work_queue()

        self.stdout.write('-----> Waiting for incoming transformation requests ...')
        for msg in pubsub.listen():
            if msg['type'] == 'message' and msg['channel'] == 'muto:queue' and msg['data'] == 'PUSH':
                self.work_queue()

    def work_queue(self):
        while True:
            data = self.redis.lpop('muto:queue')
            if data is None:
                break

            transform = json.loads(data)
            self.stdout.write('-----> Transforming {bucket}/{key} ...'.format(**transform))

            bucket = self.s3.get_bucket(transform['bucket'])
            orig_key = bucket.get_key(transform['key'])
            orig_key_base, orig_key_ext = transform['key'].rsplit('.')
            orig = BytesIO()
            orig_key.get_file(orig)
            orig_key.close()
            orig.seek(0)

            thumbnailer = get_thumbnailer(orig, relative_name=transform['key'])

            for version in transform['versions']:
                self.stdout.write('       - {identifier}'.format(**version))

                thumb = thumbnailer.get_thumbnail(version['options'], save=False)

                thumb_key = Key(bucket)
                thumb_key.key = u'{0}.{1}.{2}'.format(
                    orig_key_base,
                    version['identifier'],
                    orig_key_ext
                )
                thumb_key.content_type = 'image/jpeg'
                thumb_key.set_contents_from_string(thumb.read())
                thumb_key.set_acl('public-read')

                thumb_data = dict(
                    key=thumb_key.key,
                    width=thumb.width,
                    height=thumb.height,
                )

                self.redis.hmset('muto:{bucket}:{key}:{version}'.format(**dict(
                    bucket=transform['bucket'],
                    key=transform['key'],
                    version=version['identifier'],
                )), thumb_data)

            if transform['callback_url'] is not None:
                headers = {'content-type': 'application/json'}
                payload = {
                    'model': transform['model'],
                    'pk': transform['pk'],
                    'field': transform['field'],
                    'status': 'DONE',
                }
                requests.post(transform['callback_url'], data=json.dumps(payload), headers=headers)
