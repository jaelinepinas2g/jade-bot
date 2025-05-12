import discord
from discord.ext import commands
import os

# Carregar o token de maneira segura
token = os.getenv('DISCORD_TOKEN')

# Verificação se o token foi carregado corretamente
if not token:
    raise ValueError("ERROR: Discord token not found. Check your Secrets in Replit.")

# Configuração de intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessary to detect new members

# Bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# List of useful links
useful_links = {
    "W3Schools Python (English)": "https://www.w3schools.com/python/",
    "CS50 (Harvard Computer Science Course)": "https://cs50.harvard.edu/",
    "OOP in Python (Object-Oriented Programming)": "https://realpython.com/python3-object-oriented-programming/"
}

# Store suggestions
pending_suggestions = {
    'links': [],
    'pdfs': []
}

# When the bot is online
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')

# When a new member joins the server
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        welcome_message = (
            f"👋 Hello, {member.mention}! Welcome to the server!\n\n"
            "Here are some useful Python links to get you started:\n"
        )
        for link in useful_links:
            welcome_message += f"🔗 {link}: {useful_links[link]}\n"

        await channel.send(welcome_message)

# Command renamed to 'commands' to avoid conflict with Discord's default help
@bot.command(name='commands')
async def commands(ctx):
    help_message = (
        "🛠️ **Available Commands:**\n"
        "`!commands` - Shows this help message.\n"
        "`!links` - Sends useful Python-related links.\n"
        "`!ping` - Responds with 'Pong!' to test the bot.\n"
        "`!suggest_link <URL> <Description>` - Suggest a link to be added to the material.\n"
        "`!suggest_pdf <Description>` - Suggest a PDF to be added to the material.\n"
        "`!list_suggestions` - List all pending suggestions.\n"
        "`!approve_link <index>` - Approve a link suggestion (Admin only).\n"
        "`!approve_pdf <index>` - Approve a PDF suggestion (Admin only).\n"
    )
    await ctx.send(help_message)

# Command to send useful links
@bot.command()
async def links(ctx):
    links_message = "📌 **Useful Python Links:**\n"
    for link in useful_links:
        links_message += f"🔗 **{link}**: {useful_links[link]}\n"
    await ctx.send(links_message)

# Command to suggest a link
@bot.command()
async def suggest_link(ctx, url: str, *, description: str):
    pending_suggestions['links'].append({'url': url, 'description': description, 'author': ctx.author.name})
    await ctx.send(f"✅ Link suggestion received: {description} - {url}")

# Command to suggest a PDF
@bot.command()
async def suggest_pdf(ctx, *, description: str):
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a PDF file with your suggestion.")
        return

    attachment = ctx.message.attachments[0]
    pending_suggestions['pdfs'].append({'description': description, 'file': attachment.url, 'author': ctx.author.name})
    await ctx.send(f"✅ PDF suggestion received: {description}")

# Command to list all pending suggestions
@bot.command()
async def list_suggestions(ctx):
    if not pending_suggestions['links'] and not pending_suggestions['pdfs']:
        await ctx.send("❌ No pending suggestions.")
        return

    suggestion_message = "📋 **Pending Suggestions:**\n"
    if pending_suggestions['links']:
        suggestion_message += "\n**Links:**\n"
        for idx, suggestion in enumerate(pending_suggestions['links'], 1):
            suggestion_message += f"{idx}. {suggestion['description']} - Suggested by {suggestion['author']}\n"

    if pending_suggestions['pdfs']:
        suggestion_message += "\n**PDFs:**\n"
        for idx, suggestion in enumerate(pending_suggestions['pdfs'], 1):
            suggestion_message += f"{idx}. {suggestion['description']} - Suggested by {suggestion['author']}\n"

    await ctx.send(suggestion_message)

# Command to approve a link suggestion (Admin only)
@bot.command()
async def approve_link(ctx, index: int):
    if index < 1 or index > len(pending_suggestions['links']):
        await ctx.send("❌ Invalid link suggestion index.")
        return

    link = pending_suggestions['links'].pop(index - 1)
    useful_links[link['description']] = link['url']
    await ctx.send(f"✅ Link '{link['description']}' has been approved and added.")

# Command to approve a PDF suggestion (Admin only)
@bot.command()
async def approve_pdf(ctx, index: int):
    if index < 1 or index > len(pending_suggestions['pdfs']):
        await ctx.send("❌ Invalid PDF suggestion index.")
        return

    pdf = pending_suggestions['pdfs'].pop(index - 1)
    await ctx.send(f"✅ PDF '{pdf['description']}' has been approved and added.")

# Command to ping the bot (Test command)
@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong!')

# Start the bot
bot.run(token)
