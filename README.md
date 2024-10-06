# 1. Клонирование репозитория

Клонируйте репозиторий с исходным кодом и тестами:

```bash
git clone <URL репозитория>
cd <директория проекта>
```

# 2. Виртуальное окружение

```shell
python -m venv venv
venv/Scripts/activate
```

# 3. Запуск программы

Запуск в режиме **CLI**:

```shell
py main.py "my-user" "archive.tar" "logs.json" "start.txt"
```

# 4. Тестирование

Для запуска тестирования необходимо запустить следующий скрипт:

```shell
pytest -v
```

Для генерации отчета о покрытии тестами необходимо выполнить команду:

```shell
coverage run --branch -m pytest test_terminal.py
```

Просмотр результатов покрытия:

```shell
coverage report
```
