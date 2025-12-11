# DiscordSelf Documentation Index

Полный индекс документации DiscordSelf.

## 📚 Основные разделы

### 🚀 Начало работы
- [README](README.md) - Главная страница документации
- [Getting Started](getting-started.md) - Установка и быстрый старт
- [FAQ](faq.md) - Часто задаваемые вопросы

### 📖 API Reference
- [API Reference](api-reference.md) - Полная документация API
  - Client API
  - Models API
  - HTTP API
  - Gateway API
  - Enums
  - Exceptions

### 📘 Руководства (Guides)

#### Основные
- [Система команд](guides/commands.md) - Создание и использование команд
- [Работа с событиями](guides/events.md) - Обработка событий Discord
- [Embeds и компоненты](guides/embeds.md) - Создание красивых сообщений

#### Продвинутые
- [Голосовые функции](guides/voice.md) - Работа с голосовыми каналами
- [Cogs](guides/cogs.md) - Модульная организация кода
- [Permissions](guides/permissions.md) - Работа с правами доступа
- [Webhooks](guides/webhooks.md) - Использование webhooks
- [Threads](guides/threads.md) - Работа с нитями
- [AutoMod](guides/automod.md) - Автоматическая модерация
- [Modals](guides/modals.md) - Модальные окна

### 💡 Примеры

#### Базовые
- [Базовые примеры](examples/basic.md) - Простые примеры использования
- [Примеры команд](examples/commands.md) - Примеры создания команд
- [Примеры голоса](examples/voice.md) - Примеры голосовых функций

#### Продвинутые
- [Продвинутые примеры](examples/advanced.md) - Сложные сценарии использования

### 📝 Дополнительно
- [Changelog](changelog.md) - История изменений
- [Wiki](WIKI.md) - Вики с общей информацией

## 🔍 Быстрый поиск

### По функциональности

**Сообщения:**
- Отправка: [API Reference - send_message](api-reference.md#send_message)
- Редактирование: [API Reference - edit_message](api-reference.md#edit_message)
- Поиск: [API Reference - search_messages](api-reference.md#search_messages)

**Команды:**
- Создание: [Guides - Commands](guides/commands.md)
- Checks: [Guides - Commands - Checks](guides/commands.md#checks)
- Cooldowns: [Guides - Commands - Cooldowns](guides/commands.md#cooldowns)

**Голос:**
- Подключение: [Guides - Voice](guides/voice.md#подключение-к-голосовому-каналу)
- Воспроизведение: [Guides - Voice](guides/voice.md#воспроизведение-аудио)
- Запись: [Guides - Voice](guides/voice.md#запись-аудио)

**Embeds:**
- Создание: [Guides - Embeds](guides/embeds.md#embeds)
- Кнопки: [Guides - Embeds](guides/embeds.md#кнопки)
- Меню: [Guides - Embeds](guides/embeds.md#выпадающие-меню-select-menu)

### По задачам

**Хочу создать бота:**
1. [Getting Started](getting-started.md)
2. [Guides - Commands](guides/commands.md)
3. [Examples - Basic](examples/basic.md)

**Хочу добавить голос:**
1. [Guides - Voice](guides/voice.md)
2. [Examples - Voice](examples/voice.md)

**Хочу использовать модальные окна:**
1. [Guides - Modals](guides/modals.md)

**Хочу настроить AutoMod:**
1. [Guides - AutoMod](guides/automod.md)

**Хочу организовать код:**
1. [Guides - Cogs](guides/cogs.md)

## 📋 Структура документации

```
docs/
├── README.md              # Главная страница
├── INDEX.md              # Этот файл
├── WIKI.md               # Вики
├── getting-started.md    # Начало работы
├── api-reference.md      # API документация
├── faq.md                # FAQ
├── changelog.md          # История изменений
├── guides/               # Руководства
│   ├── commands.md
│   ├── voice.md
│   ├── events.md
│   ├── embeds.md
│   ├── cogs.md
│   ├── permissions.md
│   ├── webhooks.md
│   ├── threads.md
│   ├── automod.md
│   └── modals.md
└── examples/             # Примеры
    ├── basic.md
    ├── advanced.md
    ├── commands.md
    └── voice.md
```

## 🎯 Рекомендуемый путь обучения

1. **Начало** → [Getting Started](getting-started.md)
2. **Основы** → [Examples - Basic](examples/basic.md)
3. **Команды** → [Guides - Commands](guides/commands.md)
4. **События** → [Guides - Events](guides/events.md)
5. **Продвинутое** → [Examples - Advanced](examples/advanced.md)
6. **Справочник** → [API Reference](api-reference.md)

## 💬 Нужна помощь?

- [FAQ](faq.md) - Часто задаваемые вопросы
- [GitHub Issues](https://github.com/yourusername/discordself/issues) - Сообщить об ошибке
- [API Reference](api-reference.md) - Полная документация API

