import re
import shlex
import inspect
import asyncio
from nio import (AsyncClient, ClientConfig, RoomMessageText, InviteEvent)

class Bot():

    def __init__(self, controller, creds, config_dir='/opt/matrix'):
        self.name = controller.MATRIXBZ_BOT_NAME
        self.CHANNEL_GREETING = controller.CHANNEL_GREETING
        self.user = creds['user']
        self.password = creds['password']
        self.client = AsyncClient(creds['homeserver'], creds['user'])
        self.client.add_event_callback(self.invite_cb, InviteEvent)
        self.client.add_event_callback(self.message_cb, RoomMessageText)
        self.commands = {}
        members = inspect.getmembers(controller, predicate=inspect.ismethod)
        for member in members:
            if hasattr(member[1], 'matrixbz_method'):
                # add member[1]
                command_str = f'!{self.name} {member[0]}'
                self.commands[command_str] = member[1]
        command_prefixes = '|'.join(list(self.commands.keys()))
        self.command_regex = re.compile(f'^({command_prefixes})( .+)?$')

    async def message_cb(self, room, event):
        txt = event.body.strip()
        match = self.command_regex.match(txt)
        if match:
            command_str = match.group(1)
            command = self.commands[command_str]
            args = []
            args_str = match.group(2)
            if args_str:
                args = shlex.split(args_str)
            res = command(*args)
            await self.client.room_send(
                room_id=room.room_id, message_type='m.room.message',
                content={
                    'msgtype': 'm.text',
                    'body': str(res)})

    async def invite_cb(self, room, event):
        # TODO : Authenticated invites? / user-specific invites?
        # currently auto-joins all
        if event.membership == 'invite' and event.state_key == self.user:
            await self.client.join(room.room_id)
            await self.client.room_send(
                room_id=room.room_id, message_type='m.room.message',
                content=self.CHANNEL_GREETING)

    async def loginandsync(self):
        await self.client.login(self.password)
        await self.client.sync_forever(timeout=30000)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.loginandsync())
