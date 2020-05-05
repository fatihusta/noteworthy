import re
import shlex
import inspect
import asyncio
from nio import (AsyncClient, ClientConfig, RoomMessageText, InviteMemberEvent)

class Bot():

    def __init__(self, controller, creds, config_dir='/opt/matrix'):
        self.name = controller.MATRIXBZ_BOT_NAME
        self.CHANNEL_GREETING = controller.CHANNEL_GREETING
        self.user = creds['user']
        self.password = creds['password']
        self.client = AsyncClient(creds['homeserver'], creds['user'])
        self.client.add_event_callback(self.invite_cb, InviteMemberEvent)
        self.client.add_event_callback(self.message_cb, RoomMessageText)
        self.commands = {}
        self.msg_handler = None
        members = inspect.getmembers(controller, predicate=inspect.ismethod)
        for member in members:
            if hasattr(member[1], 'matrixbz_method'):
                # add member[1]
                command_str = f'!{self.name} {member[0]}'
                self.commands[command_str] = member[1]
            elif hasattr(member[1], 'matrixbz_msg_handler'):
                self.msg_handler = member[1]
        command_prefixes = '|'.join(list(self.commands.keys()))
        self.command_regex = re.compile(f'^({command_prefixes})( .+)?$')

    async def message_cb(self, room, event):
        txt = event.body.strip()
        context = {'room': room, 'event': event, 'client': self.client}
        match = self.command_regex.match(txt)
        if match:
            await self._execute_command(context, match)
        elif self.msg_handler:
            try:
                await self.msg_handler(context)
            except:
                return

    async def _execute_command(self, context, match):
        room = context.get('room')
        command_str = match.group(1)
        command = self.commands[command_str]
        args = []
        args_str = match.group(2)
        if args_str:
            args = shlex.split(args_str)
        try:
            res = await command(*args, context = context)
        except:
            return
        if res:
            await self.client.room_send(
                room_id=room.room_id, message_type='m.room.message',
                content={
                    'msgtype': 'm.notice',
                    'body': str(res)})

    async def invite_cb(self, room, event):
        # TODO : Authenticated invites? / user-specific invites?
        # currently auto-joins all
        if event.membership == 'invite' and event.state_key == self.user:
            await self.client.join(room.room_id)
            greeting = self._get_greeting()
            await self.client.room_send(
                room_id=room.room_id, message_type='m.room.message',
                content={
                    'msgtype': 'm.text',
                    "format": "org.matrix.custom.html",
                    'body': greeting,
                    'formatted_body': greeting})

    def _get_greeting(self):
        if self.CHANNEL_GREETING:
            return self.CHANNEL_GREETING
        msg = f"<h1>Hello!, I'm {self.name}.</h1><h3>Try some commands:</h3><ul>"
        command_strings = list(self.commands.keys())
        for cmd in command_strings:
            msg = msg + f'<li><code>{cmd}</code></li>'
        msg = msg + '</ul>'
        return msg

    async def loginandsync(self):
        await self.client.login(self.password)
        await self.client.sync_forever(timeout=30000)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.loginandsync())
