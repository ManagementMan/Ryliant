import datetime
import discord
import asyncio
#import io

class Ryliant(discord.Client):
    def __init__(self, command_prefix, mod_channel_id, verify_channel_id):
        super().__init__()
        self.command_prefix = command_prefix
        self.mod_channel_id = mod_channel_id
        self.verify_channel_id = verify_channel_id
        
        self._pending_actions = {}
    
    async def on_ready(self):
        print("[RYLIANT by EndenDragon#1337]")
        print(self.user.name)
        print(self.user.id)
        print('------')
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.split() and message.content.split()[0] == "{}verify".format(self.command_prefix):
            self._pending_actions[message.author.id] = "verify"
            await message.author.send("Please upload an image of your gear, or yourself fencing and write your organization / club affiliation.\nIf you are an instructor, contact the admins ; or post proof of your identity.\nType `done` if you're finished with sending your verification. You cannot edit after submission. I will provide reference number upon successful submission. I will also automatically submit your request after 5 minutes if you do not type `done` after your first message.")
            await message.add_reaction("☑")
        elif message.content.split() and message.content.split()[0] == "{}modmail".format(self.command_prefix):
            self._pending_actions[message.author.id] = "modmail"
            await message.author.send("Messages sent here will be visible to all moderators. They will reply back soon. Please construct your messages to be concise.\nThe next message you post here will be taken and sent. Any subsequent messages after this will not.")
            await message.delete()
        elif message.type is discord.MessageType.default and not message.guild and message.author != self.user:
            if self._pending_actions.get(message.author.id, None) == "modmail":
                channel = self.get_channel(self.mod_channel_id)
                await self._handle_dm([message], "ModMail", channel)
            elif self._pending_actions.get(message.author.id, None) == "verify":
                self.remove_from_pending_actions(message.author.id)
                channel = self.get_channel(self.verify_channel_id)
                messages = [message]
                def check(m):
                    if message.type is discord.MessageType.default and not message.guild and message.author != self.user and m.content.lower() not in ["done", ".done"] and m.channel == message.channel:
                        messages.append(m)
                    return m.content.lower() in ["done", ".done"] and m.channel == message.channel
                try:
                    await self.wait_for('message', check=check, timeout=(60.0 * 5))
                except asyncio.TimeoutError:
                    await message.channel.send("5 minutes have been elapsed since your first message. I have automatically submitted your request to the team. There is no need to type `done` now that I have sent the request.")
                await self._handle_dm(messages, "Verification", channel)
            self.remove_from_pending_actions(message.author.id)

    
    def remove_from_pending_actions(self, user_id):
        if user_id in self._pending_actions:
            del self._pending_actions[user_id]

    async def _handle_dm(self, messages, action, channel):
        content = ""
        content2 = ""
        #attachments = []
        for m in messages:
            if m.content:
                content = content + m.content + "\n"
            for a in m.attachments:
                content2 = content2 + a.url + "\n"
                # if len(attachments) > 10:
                #     continue
                # s = io.BytesIO()
                # await a.save(s)
                # s.seek(0)
                # attachments.append(discord.File(s, filename=a.filename))
        embed = discord.Embed()
        message = messages[0]
        embed.set_author(name="{}#{}".format(message.author.name, message.author.discriminator), icon_url=message.author.avatar_url)
        embed.title = "New {}! [Ref #**{}**]".format(action, message.id)
        embed.description = content
        embed.color = discord.Color.green()
        embed.set_footer(text="User ID ~ {}".format(message.author.id))
        embed.timestamp = datetime.datetime.now()
        await message.channel.send("I've forwarded your {} message to the team. Your reference number to this issue is **{}**.".format(action, message.id))
        #await message.channel.send(embed=embed)
        await channel.send(embed=embed)
        #await message.channel.send(files=attachments)
        if content2:
            await channel.send(content2)

    async def on_raw_reaction_add(self, payload):
        #print(payload.guild_id, payload.channel_id, payload.message_id, payload.emoji) 
        if payload.message_id != 592996628198195205:
         return
        server = self.get_guild(payload.guild_id)
        member = server.get_member(payload.user_id) 
        role = server.get_role(592026625034420254) 
        await member.add_roles(role) 
        currentDT = datetime.datetime.now()
        formatted_time = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        await self.get_channel(596462783713902622).send(f"" + member.name + "#" + member.discriminator + " " + str(payload.user_id ) + " added " + payload.emoji.name + " to " + str(payload.message_id) + " @ " + str(formatted_time) + "\n Joined at " + str(member.joined_at))
