import json
from django.core.cache import cache
from social_auth.db.django_models import UserSocialAuth
from app import tasks


class VkSocial:
    VK_PROVIDER = 'vk-oauth'

    def __init__(self):
        pass

    @staticmethod
    def get_access_token_and_id(request):
        if request.user.is_authenticated():
            instance = UserSocialAuth.objects.filter(provider=VkSocial.VK_PROVIDER).get(user_id=request.user.id)
            access_token = instance.tokens['access_token']
            user_vk_id = instance.uid
            return access_token, user_vk_id
        return None

    @staticmethod
    def get_userpic(user_id, user_vk_id, access_token):
        cache_key = 'userpic_%s' % user_vk_id
        userpic = cache.get(cache_key)
        if userpic is None:
            userpic_res = tasks.fetch_userpic.delay(user_id, user_vk_id, access_token)
            userpic = userpic_res.get()
            cache.set(cache_key, userpic, 60*30)
        return userpic


class MQ:
    def __init__(self):
        pass


class Rsys:
    def __init__(self):
        pass

    @staticmethod
    def rate(user_id, song_id, rating):
        import pika
        URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'
        connection = pika.BlockingConnection(pika.URLParameters(URL))
        channel = connection.channel()

        channel.queue_declare(queue='rsys', durable=True)

        data = {
            'user_id': user_id,
            'item_id': song_id,
            'rating': rating
        }

        data_json = json.dumps(data, encoding='utf-8')

        channel.basic_publish(exchange='',
                              routing_key='rsys',
                              body=data_json)

        print " [x] Sent '%s'" % data_json

        connection.close()

