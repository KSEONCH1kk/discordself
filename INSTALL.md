# Инструкция по установке

## Рекомендуемый способ установки

Используйте `pip` для установки библиотеки:

```bash
# Установка из текущей директории
pip install -e .

# Или установка зависимостей отдельно
pip install -r requirements.txt
```

## Альтернативные способы

### Установка зависимостей вручную

```bash
pip install "aiohttp>=3.8.0,<4.0.0" "websockets>=10.0"
```

### Установка для разработки

```bash
pip install -e .[dev]
```

## Проблемы при установке

Если возникают ошибки компиляции при установке `aiohttp`:

1. **Windows**: Установите Microsoft Visual C++ Build Tools
2. **Используйте предкомпилированные wheels**:
   ```bash
   pip install --only-binary :all: aiohttp websockets
   ```

3. **Или используйте conda**:
   ```bash
   conda install aiohttp websockets
   ```

## Примечание

`setup.py install` устарел и не рекомендуется. Используйте `pip install` вместо этого.

