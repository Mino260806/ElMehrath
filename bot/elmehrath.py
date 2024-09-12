import discord
from discord import Message
from discord.ext import commands

from ai.aibrain import AiBrain
from bot.submit_document import SubmitDocumentTask
from db.manager import DbManager
from file.attachment import AttachmentManager
from model.subject import Subject, lesson_catalog


class ElMehrathBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__("/", intents=intents)

        self.aibrain = AiBrain()
        self.db = DbManager()
        self.forum_catalog = {}
        self.channel_catalog = {}
        self.attachment_manager = AttachmentManager()

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

        for subject in Subject.list():
            print(f"Loading channel {subject.description.lower()}")
            channel = discord.utils.get(self.get_guild(1283377051398570004).channels, name=subject.description.lower())
            self.forum_catalog[subject] = channel
            self.channel_catalog[subject] = {}
            for thread in channel.threads:
                lesson = lesson_catalog[subject].by_description(thread.name)
                self.channel_catalog[subject][lesson] = thread

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        attachment_count = len(message.attachments)
        if attachment_count > 0:
            print(message.attachments)

            submit_task = SubmitDocumentTask(self)
            await submit_task.run(message.channel, message)

    @commands.command(name='delete')
    async def delete(self, ctx, document_id):
        self.db.delete(document_id)
        await ctx.send(f'Deleted document {document_id}!')
