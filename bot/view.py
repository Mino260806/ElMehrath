import discord

from model.subject import Subject


class AttributeSelectorView(discord.ui.View):
    def __init__(self, attr_cls, attachment, callback, on_cancel):
        super().__init__()
        self.attachment = attachment
        self.attr_cls = attr_cls
        self.callback = callback
        self.on_cancel = on_cancel

        self.generate_buttons()

    def generate_buttons(self):
        for attribute in self.attr_cls.list():
            button = discord.ui.Button(label=attribute.description, style=discord.ButtonStyle.secondary)
            button.callback = self.create_button_callback(attribute)
            self.add_item(button)
        button_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.primary)
        button_cancel.callback = self.create_cancel_callback()
        self.add_item(button_cancel)

    def create_button_callback(self, attribute):
        async def callback(interaction: discord.Interaction):
            await self.callback(self.attachment, attribute, interaction)
        return callback

    def create_cancel_callback(self):
        async def callback(interaction: discord.Interaction):
            await self.on_cancel()
        return callback


class SubjectSelectorView(AttributeSelectorView):
    def __init__(self, attachment, callback, on_cancel):
        super().__init__(Subject, attachment, callback, on_cancel)


