#
#   Purpose: Command a minecraft server
#   Created: 22/01/2022
#   Author: AlpacaSundae#0648
#
#   Commanded through slash commands in discord
#   Runs the server using a script located at "MC_DIR/MC_LAUNCH" --> default: "execs/mc_server/run.sh"
#   Requires a commanding user to have a role as specified by its ID stored in MC_ROLE 
#
# todo: status role that anyone can invoke telling if server is up, how many players, ip etc

import interactions
import subprocess
import time
import os

from interactions import Button, ButtonStyle, Modal, TextInput, TextStyleType, Permissions

MC_DIR = os.path.join(os.getcwd(), "execs/mc_server/")
MC_LAUNCH = os.path.join(MC_DIR, "run.sh")
MC_PORT = "25565"

# Variables
MC_ROLE = 1067129702235521024 # copy ID of the role given to allow mc_runner control here

# Some predefined messages
INVALID_PERMISSIONS = "You do not meet role requirements for managing \"mc_runner\""

class MCRunnerError(Exception):
    pass

class MCRunner():
    def __init__(self):
        self.proc = None
        self.start_time = None
        self._updateIP()
    
    def _updateIP(self):
        self.ip = subprocess.run(['curl', 'ifconfig.me'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    def _closeNice(self):
        closed = False
        
        if (self.proc):
            try:
                self.command("stop")
                self.proc.communicate(timeout=15)
                if (self.proc.poll() is not None):
                    closed = True
                    self.proc = None
            except subprocess.TimeoutExpired as e:
                pass
        else:
            closed = True
            
        return closed

    def _terminate(self):
        if (self.proc):
            self.proc.kill()
            self.proc = None

    def getIP(self):
        return f"{self.ip}:{MC_PORT}"

    def getDetails(self):
        raise MCRunnerError("not implemented yet sorry >.<")

    def checkPerm(self, ctx):
        return any(role == MC_ROLE for role in ctx.author.roles)

    def start(self):
        if (self.proc):
            raise MCRunnerError("Server already running")
        else:
            try:
                # Setup launch command from script file
                exec_server = ""
                with open(MC_LAUNCH, 'r') as f:
                    exec_server = f.readline().strip('\n')

                if (exec_server == ""):
                    raise MCRunnerError(f"Invalid server executable: {MC_LAUNCH}")

                # Now start the server
                self.proc = subprocess.Popen(
                    exec_server,
                    stdin =subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    cwd=MC_DIR,
                )
                self.start_time = time.time()

            except IOError as e:
                raise MCRunnerError(f"IOError: {e}")
    
    def stop(self):
        if (self.proc):
            if not self._closeNice():
                self._terminate()
        else:
            raise MCRunnerError("No server to stop")

    def command(self, command):
        if (self.proc is not None):
            self.proc.stdin.write(f'{command}\n'.encode())
        else:
            raise MCRunnerError("No server is running to command")


class MCRunnerBot(interactions.Extension):
    def __init__(self, client):
        self.client = client
        self.MCRunner = MCRunner()

    @interactions.extension_command(
        name="mc_ctl",
        description="Minecraft server controller",
        default_member_permissions=Permissions.ADMINISTRATOR,
    )
    async def mc_ctl(self, ctx):
        #start button if stopped, stop if started
            # update on press?
        #send command button --> leads to modal
        #stdout tail --> output most recent stdoutputs (if possible)
        mc_buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="mc_b_start",
                label="start",
            ),
            Button(
                style=ButtonStyle.DANGER,
                custom_id="mc_b_stop",
                label="stop",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="mc_b_cmd",
                label="send command",
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                custom_id="mc_b_out",
                label="tail stdout",
            ),
        ]
        await ctx.send(f"Minecraft ? yeah i sure hope it does ??", components=[mc_buttons])

    ## run the stopped mc server
    @interactions.extension_component("mc_b_start")
    async def start(self, ctx):
        if not self.MCRunner.checkPerm(ctx):
            await ctx.send(INVALID_PERMISSIONS)
            return

        try:
            self.MCRunner.start()
            await ctx.send(f"Server ahs been started\njoin@{self.MCRunner.getIP()}")
        except MCRunnerError as e:
            await ctx.send(f"Error starting server:\n```{e}```")


    ## stop the running mc server
    @interactions.extension_component("mc_b_stop")
    async def stop(self, ctx):
        if not self.MCRunner.checkPerm(ctx):
            await ctx.send(INVALID_PERMISSIONS)
            return

        try:
            self.MCRunner.stop()
            await ctx.send("Server closed")
        except MCRunnerError as e:
            await ctx.send(f"Error closing server:\n```{e}```")

    ## send a command to the server
    @interactions.extension_component("mc_b_cmd")
    async def cmd(self, ctx:interactions.ComponentContext):
        if not self.MCRunner.checkPerm(ctx):
            await ctx.send(INVALID_PERMISSIONS)
            return

        # create modal to allow cmd input
        modal = Modal(
            custom_id="mc_m_cmd",
            title="Enter your desired command",
            components=[
                TextInput(
                    style=TextStyleType.PARAGRAPH,
                    custom_id="mc_t_cmd",
                    label="go go bo zo:",
                ),
            ]
        )
        await ctx.popup(modal)

    # now to handle the modal
    @interactions.extension_modal("mc_m_cmd")
    async def cmd_modal(self, ctx, msg: str):
        if not self.MCRunner.checkPerm(ctx):
            await ctx.send(INVALID_PERMISSIONS)
            return

        # run command, output results
        try:
            response = self.MCRunner.command(msg)
            await ctx.send(f'command sent!\n```{response}```')
        except MCRunnerError as e:
            await ctx.send(f'command failed:\n```{e}```')

    ## tail of the servers output
    @interactions.extension_component("mc_b_out")
    async def out(self, ctx):
        try:
            response = self.MCRunner.getDetails()
            await ctx.send(f'Server says:\n```{response}```')
        except MCRunnerError as e:
            await ctx.send(f'Error getting server deets:\n```{e}```')
    

def setup(client):
    MCRunnerBot(client)