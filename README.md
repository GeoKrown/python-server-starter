# Python Server Starter

Один запуск PowerShell готує Python і базовий інструментарій для роботи ШІ з кодом, таблицями, PDF, документами та вебсторінками.

## Запуск на новому сервері

Скопіюйте всю папку на сервер. Відкрийте PowerShell у цій папці:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

Python до цього встановлювати не потрібно. Потрібні Windows x64, PowerShell 5.1+, інтернет і право встановлення програм для поточного користувача. Підтримку конкретної версії Windows визначає обрана версія Python; старі ОС можуть її не підтримувати.

Скрипт знаходить найновіший фінальний Python із класичним x64 EXE на python.org, завантажує його, перевіряє цифровий підпис Python Software Foundation та встановлює для поточного користувача. Beta/RC/alpha не вибираються. Python додається до користувацького PATH; новий PATH буде доступний у новому терміналі. Наявні Python не видаляються.

Бібліотеки встановлюються у `.venv` цієї папки, а не глобально. Запуск програми з цими бібліотеками:

```powershell
.\.venv\Scripts\python.exe C:\Apps\my_script.py
```

Для IDE/ШІ виберіть цей самий `.venv\Scripts\python.exe` як інтерпретатор.

## Набори

За замовчуванням `base`: SDK OpenAI, Anthropic, Google Gen AI; HTTP і парсинг; Playwright Chromium; pandas, NumPy, Excel; PDF, Word, PowerPoint; Pillow; FastAPI, SQLAlchemy; pytest і Ruff. Повний перелік у `packages.json`.

Додатково геодані, PostgreSQL-клієнт, Telegram і Google API:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -Profile all
```

Базовий набір не означає «всі бібліотеки Python». Локальні LLM, CUDA/PyTorch, Docker, сервер PostgreSQL, FFmpeg, Node.js та ключі API сюди не входять. Це загальний інструментарій, не автоматична міграція проєктів. Застосункам із власними зафіксованими залежностями потрібні окремі середовища (наприклад, різні версії Telegram SDK).

## Перевірка і повторне встановлення

```powershell
# Показати вибрану версію та шляхи без встановлення (потрібен інтернет)
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -Plan

# Перевірити наявне середовище без встановлення
.\.venv\Scripts\python.exe .\install_packages.py --check

# Оновити бібліотеки в поточному середовищі
.\.venv\Scripts\python.exe .\install_packages.py --refresh

# Без завантаження/перевірки Chromium
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -SkipBrowser
```

Для перевірки/оновлення розширеного набору додайте `--profile all` до Python-команди. Після успіху зберігається `requirements-<profile>-py<version>.lock.txt`. Повторний запуск використовує цей знімок; `--refresh` явно оновлює пакети. Перенесіть lock-файл разом із папкою для відтворення версій на Windows з такою самою версією Python. Це знімок pip freeze без хешів, не гарантія довічної доступності пакетів у PyPI.

## Якщо найновіший Python ще не підтримує бібліотеку

Нова версія Python іноді виходить раніше за готові wheels пакетів. Інсталятор не запускає компіляцію бібліотек і не підміняє версію Python мовчки. Він зупиниться з помилкою pip. Можна вибрати конкретний стабільний випуск, присутній на офіційній сторінці Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -PythonVersion 3.14.8
```

Це приклад вибору версії, не обіцянка сумісності всіх пакетів. Для зміни minor-версії використовуйте нову папку проєкту або збережіть стару `.venv` під іншою назвою; скрипт не перезаписує її. Якщо середовище після помилки неповне, виправте причину й повторіть запуск. Ключі/бази/налаштування застосунків інсталятор не читає.

## Перевірки розробника

```powershell
python -B -m unittest discover -s . -p test_starter.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\test-bootstrap.ps1
```

Тести перевіряють вибір офіційного релізу, відмову на неправильних даних, захист стороннього середовища, повторне використання lock і помилки інсталяції. Вони не встановлюють Python або пакети. Реальний серверний запуск потрібно перевіряти окремо.

## Джерела

- https://www.python.org/downloads/windows/
- https://docs.python.org/3/using/windows.html
- https://pip.pypa.io/en/stable/cli/pip_install/
- https://playwright.dev/python/docs/browsers

Перевірені альтернативи: https://github.com/astral-sh/uv та https://github.com/AojdevStudio/dev-bootstrap . Цей проєкт використовує стандартні Python venv/pip і не вимагає winget або uv.

## Помилка 1625 у Windows

Код 1625 означає блокування інсталяції політикою Windows. На перевіреному сервері повторний запуск PowerShell від адміністратора завершився успішно. Це не гарантує усунення всіх політик блокування: якщо помилка повторюється, перегляньте журнал у папці logs і зверніться до адміністратора сервера. Скрипт не змінює політики безпеки.

## Перевірений запуск

15.10.2026 користувацький журнал підтвердив встановлення Python 3.15.0 x64, базового набору, успішний pip check, імпорт усіх 31 бібліотеки та запуск Chromium. Розширений набір all окремо не перевірений.