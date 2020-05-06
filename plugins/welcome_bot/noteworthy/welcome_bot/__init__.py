import matrixbz
from noteworthy.notectl.plugins import NoteworthyPlugin

CHANNEL_GREETING = '''
<h1>Welcome to Noteworthy Messenger</h1>
<p>I'm <strong>WelcomeBot</strong> your personal tour guide to the Noteworthy Ecosystem.</p>
<h2>Getting started</h2>
<ul>
    <li>Join #welcome:noteworthy.im say hi</li>
    <li>Get support #support:noteworthy.im</li>
    <li>Learn about <a href="https://about.riot.im/features">Riot</a></li>
</ul>
<h2>Try more Noteworthy applications</h2>
<ul>
    <li><code>notectl install vpn</code></li>
</ul>
'''

@matrixbz.matrixbz_controller('welcomebot', channel_greeting=CHANNEL_GREETING)
class WelcomeBotController(NoteworthyPlugin):
    PLUGIN_NAME = 'welcome_bot'

    def __init__(self):
        pass

    def start(self):
        pass

Controller = WelcomeBotController
