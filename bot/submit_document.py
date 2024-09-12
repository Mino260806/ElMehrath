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

        subject_selector = SubjectSelectorView(attachment, self.on_subject_selected, self.finish)
        self.pending_message = await channel.send(f"<@{attachment.user}> please select document subject", view=subject_selector)

    async def on_subject_selected(self, attachment, subject, interaction: discord.Interaction):
        attachment.subject = subject
        print(f"Selected subject {attachment.subject.description}")
        lesson_selector = AttributeSelectorView(lesson_catalog[subject], attachment, self.on_lesson_selected, self.finish)
        self.pending_message = await interaction.message.channel.send(f'<@{attachment.user}> please select document lesson',
                                                                      view=lesson_selector)
        await interaction.message.delete()

    async def on_lesson_selected(self, attachment, lesson, interaction: discord.Interaction):
        self.pending_message = None

        attachment.lesson = lesson
        print(f"Selected lesson {attachment.lesson.description}")
        await interaction.message.delete()
        await self.on_document_submit(attachment, interaction.message.channel)
        await interaction.message.channel.send(f'Thanks for submitting a '
                                               f'{attachment.subject.description} document on '
                                               f'"{attachment.lesson.description}"')

    async def on_document_submit(self, attachment, source_channel):
        print(f"Saving document {attachment.url} to database")
        document = self.craft_document(attachment)
        document_id = self.parent.db.add_document(document)

        print(f"Forwarding document {attachment.url}")
        await self.send_document(attachment, document_id)

        print(f"Updating message id to {attachment.message_id}")
        self.parent.db.update_document_message_id(document_id, attachment.message_id)

        await self.finish()

    async def send_document(self, attachment, document_id, retry=True):
        subject = attachment.subject
        lesson = attachment.lesson
        post = await self.parent.get_submission_channel(subject, lesson)

        praise = random.choice(dialog.praise_submit).format(attachment.user)
        text = f"{praise}\ndocument id: {document_id}"
        try:
            message: Message = await post.send(text, file=File(attachment.path))
        except discord.errors.NotFound:
            if retry:
                self.parent.remove_cached_channel(subject, lesson)
                return await self.send_document(attachment, document_id, retry=False)
            else:
                return None
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

    async def finish(self):
        if self.pending_message is not None:
            await self.pending_message.channel.send("Submit cancelled")
            await self.pending_message.delete()
            self.pending_message = None
        self.attachment_manager.clear()
