import datetime
import time

import discord
from discord import Message, Guild, Member
from discord.ext import commands, tasks
from discord.ext.commands import Command
from sqlalchemy.orm import Query

from ai.aibrain import AiBrain
from bot.submit_document import SubmitDocumentTask
from db.manager import DbManager
from file.attachment import AttachmentManager
from model.subject import Subject, lesson_catalog
from util import dt_utils

SUBMIT_CHANNELS = ["submit", "test"]
DAILY_CHECKUP_CHANNEL = "daily-checkup"


class ElMehrathBot(commands.Bot):
    def __init__(self):

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__("!", intents=intents)

        self.aibrain = AiBrain()
        self.db = DbManager()
        self.forum_catalog = {}
        self.channel_catalog = {}
        self.attachment_manager = AttachmentManager()
        self.my_guild: Guild | None = None

        self.setup_commands()

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

        self.daily_checkup.start()

        await self.ensure_add_users()

        print("I am ready")

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

    @tasks.loop(time=datetime.time(hour=18))
    async def daily_checkup(self):
        print("Performing daily checkup")
        channel = self.get_checkup_channel()

        async def inactive_callback(students: Query):
            if students.count() == 0:
                await channel.send("Daily checkup result: All users are active!")
                return
            text = []
            for student in students:
                print(f"{student.id}.last_contribution_date is {student.last_contribution_date}")
                await self.remove_contributor(student.id)
                text.append(f"<@{student.id}>")
            students_raw = ", ".join(text)
            await channel.send(f"{students_raw}, you no longer have access to our valuable documents, "
                               f"submit a resource in #submit to renew your access")

        await self.db.find_inactive_users(inactive_callback)

    async def ensure_add_users(self):
        for member in self.my_guild.members:
            if member.id != self.user.id:
                self.db.add_student(member.id, member.joined_at, can_exist=True)

        async def active_callback(students: Query):
            for student in students:
                await self.give_contributor(student.id)

        await self.db.find_active_users(active_callback)

    async def give_contributor(self, member_id, notify_success=False):
        contributor_role = discord.utils.get(self.my_guild.roles, name="contributor")
        member: Member | None = await self.my_guild.fetch_member(member_id)
        if member is not None:
            if contributor_role not in member.roles:
                print(f"Giving contributor role to {member.name}")
                await member.add_roles(contributor_role)
                if notify_success:
                    channel = self.get_checkup_channel()
                    await channel.send(f"{member.mention}, you regained access to our valuable documents. "
                                       f"Thanks for contributing!")
            else:
                print(f"Member {member.name} is already contributor")

    async def remove_contributor(self, member_id):
        contributor_role = discord.utils.get(self.my_guild.roles, name="contributor")
        member: Member | None = await self.my_guild.fetch_member(member_id)
        if member is not None:
            if contributor_role in member.roles:
                print(f"Member {member.mention} is no longer contributor")
                await member.remove_roles(contributor_role)

    def setup_commands(self):
        @self.event
        async def on_member_join(member: Member):
            channel = discord.utils.get(member.guild.text_channels, name='welcome')
            if channel:
                await channel.send(f"Welcome to {self.my_guild.name}, {member.mention}!"
                                   f"To ensure you retain access to our valuable documents, "
                                   f"please make sure to share your own documents on a **weekly** basis!")
            self.db.add_student(member.id, member.joined_at)
            await self.give_contributor(member.id)

    def get_checkup_channel(self):
        return discord.utils.get(self.my_guild.channels, name=DAILY_CHECKUP_CHANNEL)
