import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Command

from ai.aibrain import AiBrain
from bot.submit_document import SubmitDocumentTask
from db.manager import DbManager
from file.attachment import AttachmentManager
from model.subject import Subject, lesson_catalog


SUBMIT_CHANNELS = ["submit", "test"]


class ElMehrathBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__("!", intents=intents)

        self.aibrain = AiBrain()
        self.db = DbManager()
        self.forum_catalog = {}
        self.channel_catalog = {}
        self.attachment_manager = AttachmentManager()
        self.my_guild = None

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

        self.my_guild = self.get_guild(1283377051398570004)

        for subject in Subject.list():
            print(f"Loading channel {subject.description.lower()}")
            channel = discord.utils.get(self.my_guild.channels, name=subject.description.lower())
            self.forum_catalog[subject] = channel
            self.channel_catalog[subject] = {}
            for thread in channel.threads:
                lesson = lesson_catalog[subject].by_description(thread.name)
                self.channel_catalog[subject][lesson] = thread

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        if message.channel.name in SUBMIT_CHANNELS:
            attachment_count = len(message.attachments)
            if attachment_count > 0:
                print(message.attachments)

                submit_task = SubmitDocumentTask(self)
                await submit_task.run(message.channel, message)

            if message.content.startswith("!delete"):
                split = message.content.split()
                if len(split) >= 2:
                    await self.delete(message.channel, message.author, split[1])

    async def get_submission_channel(self, subject, lesson, force_create=True):
        if force_create and lesson not in self.channel_catalog[subject]:
            threadwithmessage = await self.forum_catalog[subject].create_thread(
                name=lesson.description, content=lesson.description)
            post = threadwithmessage.thread
            self.channel_catalog[subject][lesson] = post
        else:
            post = self.channel_catalog[subject].get(lesson)
        return post

    def remove_cached_channel(self, subject, lesson):
        if subject in self.channel_catalog and lesson in self.channel_catalog[subject]:
            del self.channel_catalog[subject][lesson]

    async def delete(self, source_channel, author, document_id):
        print("Starting delete")
        if not author.guild_permissions.administrator:
            await source_channel.send(f'You are not an administrator')
        try:
            document_id = int(document_id)
        except ValueError:
            await source_channel.send(f'Invalid id {document_id}')
            return
        document = self.db.delete(document_id)
        if document is not None:
            subject = Subject(document.subject)
            lesson = lesson_catalog[subject](document.lesson)
            channel = await self.get_submission_channel(subject, lesson, force_create=False)
            message = await channel.fetch_message(document.message_id)
            await message.delete()
            await source_channel.send(f'Deleted document {document_id}!')
        else:
            await source_channel.send(f'No such document!')
