import interactions
import subprocess

from interactions import Button, ButtonStyle

class Control(interactions.Extension):
    def __init__(self, client):
        self.client = client

    @interactions.extension_command(
        name="ipv4",
        description="I neeeeeeed itttttt",
    )
    async def getIPv4Addr(self, ctx):
        ip_addr = subprocess.run(['curl', 'ifconfig.me'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        await ctx.send(f'The IPv4 u desire so much is: {ip_addr}')

def setup(client):
    Control(client)