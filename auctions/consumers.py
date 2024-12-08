import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.auction_group_name = f'auction_{self.auction_id}'

        # Join auction group
        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave auction group
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("-------------------------text_data_json :", text_data_json)
        message_type = text_data_json.get('type')
        print("-------------------------message_type :", message_type)

        # Call the appropriate handler based on the message type
        if message_type == 'auction_update':
            await self.auction_update(text_data_json)
        

    async def auction_update(self, event):
        print("-------------------------event :", event)
        current_bid = event['current_bid']
        print("-------------------------current_bid :", current_bid)
        current_bidder = event['current_bidder']
        print("-------------------------current_bidder :", current_bidder)
        avatar_url = event['avatar_url']
        print("-------------------------avatar_url :", avatar_url)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'auction_update',
            'current_bid': current_bid,
            'current_bidder': current_bidder,
            'avatar_url': avatar_url  # Adjust this field based on your actual model
        
        }))

    
