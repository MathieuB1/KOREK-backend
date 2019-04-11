from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        if not self.scope['user'] or self.scope['user'] is AnonymousUser:
            await self.close(code=4003)

        self.event_group_name = 'event_%s' % self.scope['user']

        # Join event group
        await self.channel_layer.group_add(
            self.event_group_name,
            self.channel_name
        )

        #await self.accept()
        await self.accept(self.scope['subprotocols'][0])

    async def disconnect(self, close_code):
        # Leave event group
        await self.channel_layer.group_discard(
            self.event_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to event group
        await self.channel_layer.group_send(
            self.event_group_name,
            {
                'type': 'event_message',
                'message': message
            }
        )

    # Receive message from event group
    async def event_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))