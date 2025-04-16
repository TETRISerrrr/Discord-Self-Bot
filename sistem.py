import discord
from discord.ext import commands
import aiohttp
import time
import asyncio
import psutil
import os
from datetime import datetime  # Импорт datetime

class Main(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

client = Main(
    command_prefix="/",
    intents=discord.Intents.all(),
    help_command=None
)

subscriptions = {}
administrators = set()

def load_subscriptions():
    global subscriptions
    try:
        with open(r" user_base.txt", "r") as file: # дириктроия файла user_base.txt
            subscriptions = {}
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) != 2: 
                    print(f"Неверный формат строки: {line}")
                    continue
                stored_user_id, expiry_date = parts
                stored_user_id = stored_user_id.strip()
                expiry_date = expiry_date.strip()
                subscriptions[stored_user_id] = datetime.strptime(expiry_date, "%Y-%m-%d").date()
    except FileNotFoundError:
        print("Файл user_base.txt не найден.")

def load_administrators():
    global administrators
    try:
        with open(r"admins_base.txt", "r") as file: # дириктроия файла admins_base.txt
            administrators = {line.strip() for line in file if line.strip().isdigit()}
    except FileNotFoundError:
        print("Файл admins_base.txt не найден.")

def check_subscription(user_id):
    expiry_date = subscriptions.get(str(user_id))
    if expiry_date is not None:
        return expiry_date >= datetime.today().date(), expiry_date
    return False, None

def is_admin(user_id):
    return str(user_id) in administrators

@client.event
async def on_ready():
    print("Бот запущен")
    load_subscriptions()
    load_administrators()
    await client.tree.sync()  # Синхронизация команд
    print("Команды синхронизированы.")
    print("-------------------------")

@client.tree.command(name="s-text", description="Отправить сообщение от имени бота.")
async def command_s_text(interaction: discord.Interaction, text: str):
    has_subscription, expiry_date = check_subscription(interaction.user.id)
    if not has_subscription:
        await interaction.response.send_message(
            content="Ваша подписка истекла или у вас её нет. Пожалуйста, обновите подписку для доступа к команде.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(content=f"{interaction.user.mention}{text}", ephemeral=True)
    await interaction.followup.send(content=f"{text}", ephemeral=False)

@client.tree.command(name="reload_base", description="Обновляет базу данных подписок.")
async def command_reload_base(interaction: discord.Interaction):
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            content="Хей! Команда не доступна для вас!",
            ephemeral=True
        )
        return

    load_subscriptions()
    await interaction.response.send_message(
        content="База данных подписок обновлена.",
        ephemeral=True
    )

@client.tree.command(name="s-info", description="Информация о боте и статусе подписки.")
async def command_s_info(interaction: discord.Interaction):
    has_subscription, expiry_date = check_subscription(interaction.user.id)
    
    if has_subscription:
        subscription_status = f"Подписка: Присутствует, закончится: {expiry_date.strftime('%Y-%m-%d')}"
    else:
        subscription_status = "Подписка: Отсутствует"
    
    info_text = (
        f"**Владелец бота:** *TETRISerrr*\n"
        f"**Код написал:** *TETRISerrr*\n"
        "\n"
        f"{subscription_status}"
    )
    
    await interaction.response.send_message(
        content=info_text,
        ephemeral=True
    )

@client.tree.command(name="s-button", description="Создать приватную кнопку для отправки сообщения от имени бота, видимую всем.")
async def command_s_button(interaction: discord.Interaction, text: str):
    has_subscription, _ = check_subscription(interaction.user.id)
    if not has_subscription:
        await interaction.response.send_message(
            content="Ваша подписка истекла или у вас её нет. Пожалуйста, обновите подписку для доступа к команде.",
            ephemeral=True
        )
        return

    class PublicButtonView(discord.ui.View):
        def __init__(self, user_id, text):
            super().__init__(timeout=None)
            self.user_id = user_id
            self.text = text

        @discord.ui.button(label="Отправить", style=discord.ButtonStyle.primary)
        async def public_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
            if interaction_button.user.id == self.user_id:
                await interaction_button.response.send_message(content=self.text)
            else:
                await interaction_button.response.send_message("У вас закончилась подписка или у вас её нет! Информация - /s-info", ephemeral=True)

    view = PublicButtonView(interaction.user.id, text)
    await interaction.response.send_message(
        content="Нажмите на кнопку ниже, чтобы отправить сообщение от имени бота, видимое всем.", view=view, ephemeral=True
    )

@client.tree.command(name="autoraid", description="Automatically send raid messages.")
async def command_autoraid(interaction: discord.Interaction, count: int):
    user_id = str(interaction.user.id)
    has_subscription, _ = check_subscription(user_id)

    if not has_subscription:
        await interaction.response.send_message("You don't have a subscription.", ephemeral=True)
        return

    await interaction.response.send_message("Starting raid...", ephemeral=True)

    message = (
        "░██████╗██╗░██████╗████████╗███████╗███╗░░░███╗░░░░░░██╗░░██╗\n"
        "██╔════╝██║██╔════╝╚══██╔══╝██╔════╝████╗░████║░░░░░░╚██╗██╔╝\n"
        "╚█████╗░██║╚█████╗░░░░██║░░░█████╗░░██╔████╔██║█████╗░╚███╔╝░\n"
        "░╚═══██╗██║░╚═══██╗░░░██║░░░██╔══╝░░██║╚██╔╝██║╚════╝░██╔██╗░\n"
        "██████╔╝██║██████╔╝░░░██║░░░███████╗██║░╚═╝░██║░░░░░░██╔╝╚██╗\n"
        "╚═════╝░╚═╝╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░░░░╚═╝░░░░░░╚═╝░░╚═╝\n\n"

        "██████╗░░█████╗░██╗██████╗░░░░░░░██████╗░░█████╗░████████╗\n"
        "██╔══██╗██╔══██╗██║██╔══██╗░░░░░░██╔══██╗██╔══██╗╚══██╔══╝\n"
        "██████╔╝███████║██║██║░░██║█████╗██████╦╝██║░░██║░░░██║░░░\n"
        "██╔══██╗██╔══██║██║██║░░██║╚════╝██╔══██╗██║░░██║░░░██║░░░\n"
        "██║░░██║██║░░██║██║██████╔╝░░░░░░██████╦╝╚█████╔╝░░░██║░░░\n"
        "╚═╝░░╚═╝╚═╝░░╚═╝╚═╝╚═════╝░░░░░░░╚═════╝░░╚════╝░░░░╚═╝░░░\n\n"


        "@everyone @here \n"
    )
    for _ in range(count):
        await interaction.followup.send(content=message)
        await asyncio.sleep(7)

client.run("") # Токен бота