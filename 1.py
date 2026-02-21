import discord
from discord.ext import commands
import asyncio
import subprocess
import re
import os

# ============================================
# НАСТРОЙКИ БОТА - ЗДЕСЬ УКАЖИТЕ ВАШ ТОКЕН!
# ============================================
TOKEN = "DARKTEST"  # <--- ВСТАВЬТЕ ВАШ ТОКЕН ЗДЕСЬ!
# Пример: TOKEN = "MTE4NzU5NjQ3NDQwNjE5ODU5OA.GfTqJz.abcdefghijklmnopqrstuvwxyz"
# ============================================

PREFIX = '!'
ALLOWED_CHANNEL_ID = 1425889109762900039  # ID канала, где можно использовать команду

# Настройки безопасности
MAX_TIME = 300  # Максимальное время в секундах
MIN_PORT = 1
MAX_PORT = 65535

# Валидация IP
def validate_ip(ip):
    """Проверка корректности IPv4 адреса"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    
    return True

def validate_port(port):
    """Проверка корректности порта"""
    if not port.isdigit():
        return False
    
    port_num = int(port)
    return MIN_PORT <= port_num <= MAX_PORT

def validate_time(time_str):
    """Проверка корректности времени"""
    if not time_str.isdigit():
        return False
    
    time_num = int(time_str)
    return 1 <= time_num <= MAX_TIME

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user.name} успешно запущен!')
    print(f'📊 ID бота: {bot.user.id}')
    print(f'📌 Разрешённый канал ID: {ALLOWED_CHANNEL_ID}')
    print(f'⚡ Префикс команд: {PREFIX}')
    print('========================================')

@bot.command(name='neo')
async def neo_command(ctx, ip: str = None, port: str = None, time: str = None):
    """Выполняет команду neo с указанными параметрами
    
    Использование: !neo <айпи> <порт> <время>
    Пример: !neo 123.123.123.123 80 60
    """
    
    # Проверка на разрешённый канал
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send(f"❌ Эта команда доступна только в определенном канале!")
        return
    
    # Проверка наличия всех аргументов
    if ip is None or port is None or time is None:
        await ctx.send("❌ Неправильный формат команды!\n"
                      f"Используйте: `{PREFIX}neo <айпи> <порт> <время>`\n"
                      f"Пример: `{PREFIX}neo 123.123.123.123 80 60`")
        return
    
    # Валидация входных данных
    if not validate_ip(ip):
        await ctx.send("❌ Неверный IP-адрес! Укажите корректный IPv4 адрес.")
        return
    
    if not validate_port(port):
        await ctx.send(f"❌ Неверный порт! Порт должен быть числом от {MIN_PORT} до {MAX_PORT}.")
        return
    
    if not validate_time(time):
        await ctx.send(f"❌ Неверное время! Время должно быть числом от 1 до {MAX_TIME} секунд.")
        return
    
    try:
        # Подготовка команды
        port_int = int(port)
        time_int = int(time)
        
        # Формирование команды для выполнения
        cmd = ['./neoprotect', ip, str(port_int), '300', '1000', str(time_int)]
        
        # Отправка начального сообщения
        loading_msg = await ctx.send(f"⚡ Запускаю neo-protect...\n"
                                     f"IP: `{ip}`\n"
                                     f"Порт: `{port_int}`\n"
                                     f"Время: `{time_int} сек`")
        
        # Выполнение команды
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Ждём завершения процесса
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Успешное выполнение
                await loading_msg.edit(content=f"✅ neo-protect успешно запущен!\n"
                                             f"IP: `{ip}`\n"
                                             f"Порт: `{port_int}`\n"
                                             f"Время: `{time_int} сек`\n"
                                             f"Код возврата: {process.returncode}")
                
                # Логирование вывода (опционально)
                if stdout:
                    print(f"STDOUT: {stdout.decode()}")
                if stderr:
                    print(f"STDERR: {stderr.decode()}")
                    
            else:
                # Ошибка выполнения
                await loading_msg.edit(content=f"❌ Ошибка при выполнении neo-protect!\n"
                                             f"Код ошибки: {process.returncode}\n"
                                             f"Ошибка: {stderr.decode() if stderr else 'Неизвестная ошибка'}")
                
        except FileNotFoundError:
            await loading_msg.edit(content="❌ Ошибка: Файл neoprotect не найден!")
        except Exception as e:
            await loading_msg.edit(content=f"❌ Произошла ошибка: {str(e)}")
            
    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка: {str(e)}")

@bot.command(name='neo_help')
async def neo_help(ctx):
    """Показывает справку по команде neo"""
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    
    help_text = (
        f"**Команда {PREFIX}neo**\n"
        "Запускает neo-protect на сервере\n\n"
        f"**Использование:** `{PREFIX}neo <айпи> <порт> <время>`\n"
        "**Пример:** `!neo 123.123.123.123 80 60`\n\n"
        "**Параметры:**\n"
        "- `айпи`: IPv4 адрес (например, 123.123.123.123)\n"
        f"- `порт`: номер порта (от {MIN_PORT} до {MAX_PORT})\n"
        f"- `время`: время в секундах (от 1 до {MAX_TIME})\n\n"
        f"**Доступно только в этом канале!**"
    )
    
    await ctx.send(help_text)

@bot.command(name='neo_info')
async def neo_info(ctx):
    """Показывает информацию о текущих настройках"""
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return
    
    info_text = (
        f"**Информация о neo-бот:**\n"
        f"Разрешённый канал: <#{ALLOWED_CHANNEL_ID}>\n"
        f"Максимальное время: {MAX_TIME} секунд\n"
        f"Диапазон портов: {MIN_PORT}-{MAX_PORT}\n"
        f"Префикс команд: {PREFIX}\n"
        f"Доступные команды: {PREFIX}neo, {PREFIX}neo_help, {PREFIX}neo_info"
    )
    
    await ctx.send(info_text)

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Недостаточно аргументов! Используйте `{PREFIX}neo_help` для справки.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Игнорируем неизвестные команды
    else:
        await ctx.send(f"❌ Произошла ошибка: {str(error)}")

# Запуск бота
if __name__ == "__main__":
    # Проверка наличия токена
    if TOKEN == "ВАШ_ТОКЕН_БОТА_ЗДЕСЬ" or not TOKEN:
        print("=" * 50)
        print("❌ ОШИБКА: Укажите токен бота!")
        print("=" * 50)
        print("\nИнструкция:")
        print("1. Создайте бота на https://discord.com/developers/applications")
        print("2. Включите все необходимые разрешения:")
        print("   - MESSAGE CONTENT INTENT")
        print("   - PRESENCE INTENT (опционально)")
        print("   - SERVER MEMBERS INTENT (опционально)")
        print("3. Скопируйте токен из раздела 'Bot'")
        print("\n4. Вставьте токен в строку 12 файла:")
        print(f"   TOKEN = \"ВАШ_ТОКЕН_БОТА_ЗДЕСЬ\"")
        print("\n5. Запустите бота снова:")
        print("   python3 bot.py")
        print("=" * 50)
    else:
        print("=" * 50)
        print("🚀 Запуск бота...")
        print("=" * 50)
        bot.run(TOKEN)
