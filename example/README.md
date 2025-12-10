# Примеры использования DiscordSelf

Эта папка содержит примеры использования различных функций библиотеки DiscordSelf.

## Файлы с примерами

### 1. `example_converters.py`
Примеры использования конвертеров:
- `RoleConverter` - конвертация ролей
- `EmojiConverter` - конвертация эмодзи
- `Greedy` - множественные аргументы
- `Literal` - литеральные значения

**Использование:**
```bash
python example/example_converters.py
```

### 2. `example_help.py`
Пример использования Help Command Generator:
- Автоматическая генерация справки
- Команда `!help` для всех команд
- Команда `!help <команда>` для конкретной команды

**Использование:**
```bash
python example/example_help.py
```

### 3. `example_cooldowns.py`
Примеры использования Cooldowns:
- Ограничение использования команд
- Различные типы cooldown (per user, per guild, per channel, global)
- Обработка ошибок cooldown

**Использование:**
```bash
python example/example_cooldowns.py
```

### 4. `example_tasks.py`
Примеры использования Tasks (периодические задачи):
- Задачи с разными интервалами
- `before_loop` и `after_loop` хуки
- Обработка ошибок в задачах

**Использование:**
```bash
python example/example_tasks.py
```

### 5. `example_views.py`
Примеры использования Views (UI Components):
- Кнопки (Buttons)
- Выпадающие меню (Select Menus)
- Кастомные View

**Использование:**
```bash
python example/example_views.py
```

### 6. `example_ffmpeg.py`
Примеры использования FFmpeg для воспроизведения аудио:
- Воспроизведение PCM аудио
- Воспроизведение Opus аудио
- Работа с различными форматами

**Требования:**
- FFmpeg должен быть установлен в системе

**Использование:**
```bash
python example/example_ffmpeg.py
```

### 7. `example_youtube.py`
Примеры использования YouTube и URL streaming:
- Воспроизведение YouTube видео
- Воспроизведение аудио из URL
- Команды для управления воспроизведением

**Требования:**
- `yt-dlp` должен быть установлен (`pip install yt-dlp`)

**Использование:**
```bash
python example/example_youtube.py
```

### 8. `example_audio_effects.py`
Примеры использования Audio Effects:
- Регулировка громкости (`VolumeTransformer`)
- Аудио фильтры (`LowPassFilter`)
- Комбинация эффектов

**Использование:**
```bash
python example/example_audio_effects.py
```

### 9. `example_recording.py`
Примеры использования Recording (запись аудио):
- Запись аудио из голосового канала
- Запись конкретного пользователя
- Запись нескольких пользователей

**Требования:**
- `opuslib` должен быть установлен для декодирования

**Использование:**
```bash
python example/example_recording.py
```

## Настройка

Перед запуском примеров:

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Установите дополнительные зависимости для Voice:
```bash
pip install pynacl opuslib yt-dlp
```

3. Установите FFmpeg (для аудио примеров):
- Windows: https://ffmpeg.org/download.html
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

4. Замените `YOUR_TOKEN_HERE` на ваш Discord токен в каждом файле

5. Замените `GUILD_ID` и `CHANNEL_ID` на реальные ID вашего сервера и канала

## Примечания

- Все примеры требуют действительный Discord токен
- Для Voice примеров нужны права на подключение к голосовым каналам
- Некоторые функции требуют дополнительные библиотеки (см. требования выше)
- Примеры предназначены для демонстрации возможностей библиотеки

