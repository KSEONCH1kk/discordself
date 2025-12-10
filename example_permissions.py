"""Пример использования Permissions calculator"""

from discordself import Client, Intents
from discordself.permissions import (
    Permissions,
    PermissionCalculator,
    has_permission,
    has_any_permission,
    has_all_permissions
)


# Пример 1: Проверка permissions
permissions_value = 268435456  # Пример значения permissions

# Создать объект Permissions
perms = PermissionCalculator.from_value(permissions_value)

# Проверить наличие конкретного permission
if has_permission(perms, Permissions.SEND_MESSAGES):
    print("✅ Пользователь может отправлять сообщения")

if has_permission(perms, Permissions.KICK_MEMBERS):
    print("✅ Пользователь может кикать участников")

# Проверить наличие хотя бы одного permission
if has_any_permission(perms, Permissions.SEND_MESSAGES, Permissions.VIEW_CHANNEL):
    print("✅ Пользователь может отправлять сообщения или просматривать канал")

# Проверить наличие всех permissions
if has_all_permissions(perms, Permissions.SEND_MESSAGES, Permissions.VIEW_CHANNEL):
    print("✅ Пользователь может отправлять сообщения И просматривать канал")


# Пример 2: Работа с permissions
base_perms = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL

# Добавить permission
new_perms = PermissionCalculator.add_permission(base_perms, Permissions.MANAGE_MESSAGES)
print(f"Новые permissions: {PermissionCalculator.get_permission_list(new_perms)}")

# Удалить permission
new_perms = PermissionCalculator.remove_permission(new_perms, Permissions.MANAGE_MESSAGES)
print(f"После удаления: {PermissionCalculator.get_permission_list(new_perms)}")


# Пример 3: Вычисление overwrite
base = Permissions.SEND_MESSAGES | Permissions.VIEW_CHANNEL
allow = Permissions.KICK_MEMBERS
deny = Permissions.SEND_MESSAGES

result = PermissionCalculator.calculate_overwrite(base, allow, deny)
print(f"Итоговые permissions: {PermissionCalculator.get_permission_list(result)}")
# Результат: VIEW_CHANNEL, KICK_MEMBERS (SEND_MESSAGES удален через deny)


# Пример 4: Проверка permissions в команде
async def check_user_permissions(ctx):
    """Пример проверки permissions пользователя"""
    # В реальном коде нужно получить permissions из Member
    user_perms = 268435456  # Пример
    
    if has_permission(user_perms, Permissions.MANAGE_MESSAGES):
        await ctx.send("Вы можете управлять сообщениями")
    else:
        await ctx.send("❌ У вас нет прав на управление сообщениями")


# Пример 5: Получение списка permissions для текстовых каналов
text_perms = PermissionCalculator.get_text_permissions()
print(f"Permissions для текстовых каналов: {len(text_perms)}")

voice_perms = PermissionCalculator.get_voice_permissions()
print(f"Permissions для голосовых каналов: {len(voice_perms)}")

mod_perms = PermissionCalculator.get_moderation_permissions()
print(f"Permissions для модерации: {len(mod_perms)}")

