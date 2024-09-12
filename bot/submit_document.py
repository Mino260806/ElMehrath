import random
import discord
from discord import Message, File

from db.document import Document
from bot.view import AttributeSelectorView, SubjectSelectorView
from file.attachment import AttachmentManager
from model import dialog
from model.subject import lesson_catalog


class SubmitDocumentTask:
    def __init__(self, parent):
        self.attachment_manager = AttachmentManager()
        self.parent = parent
        self.pending_message = None

    async def run(self, channel, message: Message):
        for attachment in message.attachments:
            self.attachment_manager.download(attachment.url,
                                             sent_date=message.created_at,
                                             filename=attachment.filename,
                                             description=message.content,
                                             user=message.author.id)

        attachment = self.attachment_manager.list[0]

        subject_selector = SubjectSelectorView(attachment, self.on_subject_selected, self.destroy)
        self.pending_message = await channel.send(f"<@{attachment.user}> please select document subject", view=subject_selector)

    async def on_subject_selected(self, attachment, subject, interaction: discord.Interaction):
        attachment.subject = subject
        print(f"Selected subject {attachment.subject.description}")
        lesson_selector = AttributeSelectorView(lesson_catalog[subject], attachment, self.on_lesson_selected, self.destroy)
        self.pending_message = await interaction.message.channel.send(f'<@{attachment.user}> please select document lesson',
                                                                      view=lesson_selector)
        await interaction.message.delete()

    async def on_lesson_selected(self, attachment, lesson, interaction: discord.Interaction):
        self.pending_message = None

        attachment.lesson = lesson
        print(f"Selected lesson {attachment.lesson.description}")
        await interaction.message.channel.send(f'Thanks for submitting a '
                                               f'{attachment.subject.description} document on '
                                               f'"{attachment.lesson.description}"')
        await interaction.message.delete()
        await self.on_document_submit(attachment)

    async def on_document_submit(self, attachment):
        print(f"Forwarding document {attachment.url}")
        await self.send_document(attachment)

        print(f"Saving document {attachment.url} to database")
        document = self.craft_document(attachment)
        self.parent.db.add_document(document)

        await self.destroy()

    async def send_document(self, attachment):
        subject = attachment.subject
        lesson = attachment.lesson
        if lesson not in self.parent.channel_catalog[subject]:
            threadwithmessage = await self.parent.forum_catalog[subject].create_thread(
                name=lesson.description, content=lesson.description)
            post = threadwithmessage.thread
            self.parent.channel_catalog[subject][lesson] = post
        else:
            post = self.parent.channel_catalog[subject][lesson]

        text = random.choice(dialog.praise_submit).format(attachment.user)
        message: Message = await post.send(text, file=File(attachment.path))
        attachment.message_id = message.id
        return message

    @staticmethod
    def craft_document(attachment):
        return Document(
            url=attachment.url,
            message_id=attachment.message_id,
            filename=attachment.filename,
            user=attachment.user,
            subject=attachment.subject.value,
            lesson=attachment.lesson.value,
            author=None,
            highschool=None,
            description=attachment.description,
            sent_date=attachment.sent_date,
        )

    async def destroy(self):
        if self.pending_message is not None:
            await self.pending_message.channel.send("Submit cancelled")
            await self.pending_message.delete()
            self.pending_message = None
        self.attachment_manager.clear()
