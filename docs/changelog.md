# Changelog

История изменений DiscordSelf.

## [1.0.0] - 2024-12-10

### Добавлено

#### Основные функции
- ✅ Полная поддержка Discord REST API
- ✅ WebSocket Gateway с автоматическим переподключением
- ✅ Система команд с автоматическим парсингом аргументов
- ✅ Cogs система для модульной организации
- ✅ Система проверок (checks) и cooldowns
- ✅ Help команды
- ✅ Обработка ошибок команд

#### Голосовые функции
- ✅ Подключение к голосовым каналам
- ✅ Воспроизведение аудио (PCM и Opus)
- ✅ FFmpeg интеграция
- ✅ YouTube поддержка
- ✅ Запись аудио
- ✅ Аудио эффекты и фильтры

#### Модели данных
- ✅ User, Guild, Channel, Message, Member, Role, Emoji
- ✅ VoiceState, Attachment, Invite
- ✅ Integration, StageInstance, ScheduledEvent
- ✅ Interaction, AutoModAction, AutoModRule

#### Дополнительные функции
- ✅ Embeds и компоненты (кнопки, меню)
- ✅ Views система
- ✅ Webhooks
- ✅ Threads (полная поддержка)
- ✅ Modals
- ✅ AutoMod API
- ✅ Tasks/Loops
- ✅ Permissions calculator

#### API методы
- ✅ Сообщения (отправка, редактирование, удаление, поиск)
- ✅ Каналы (создание, изменение, удаление)
- ✅ Гильдии (управление)
- ✅ Участники и роли
- ✅ Реакции
- ✅ Webhooks
- ✅ Threads
- ✅ AutoMod
- ✅ Scheduled Events
- ✅ Stage Instances
- ✅ Integrations
- ✅ Invites

#### Инфраструктура
- ✅ Rate limit менеджер
- ✅ Кэширование объектов
- ✅ Шардирование
- ✅ Логирование
- ✅ Обработка исключений

### Известные ограничения

- ❌ Slash Commands (не поддерживаются для selfbot)
- ❌ Application Commands (не поддерживаются для selfbot)

### Примечания

- Библиотека находится в стадии Beta
- Использование selfbot нарушает ToS Discord
- Используйте на свой риск

