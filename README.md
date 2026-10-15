# Python Server Starter

Один запуск PowerShell готує Python і базовий інструментарій для роботи ШІ з кодом, таблицями, PDF, документами та вебсторінками.

## Запуск на новому сервері

На сервері відкрийте **Windows PowerShell від імені адміністратора** під тим користувачем, який працюватиме з Python (Пуск → PowerShell → Запуск від імені адміністратора). Вставте весь блок нижче. Python і Git заздалегідь не потрібні.

Команда завантажує поточну версію цього репозиторію з GitHub, розпаковує її на робочий стіл і запускає встановлення. Якщо папка вже існує, вона зупиниться без перезапису ваших файлів.

```powershell
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
$starterRoot = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Python-Server-Starter'
if (Test-Path -LiteralPath $starterRoot) {
    throw "Папка вже існує: $starterRoot. Для повторного запуску використайте setup.ps1 з наявної папки."
}
$starterZip = Join-Path ([IO.Path]::GetTempPath()) ('python-starter-' + [guid]::NewGuid().ToString('N') + '.zip')
try {
    Invoke-WebRequest 'https://github.com/GeoKrown/python-server-starter/archive/refs/heads/main.zip' -OutFile $starterZip -UseBasicParsing -TimeoutSec 120
    Expand-Archive -LiteralPath $starterZip -DestinationPath $starterRoot
    $starterProject = Join-Path $starterRoot 'python-server-starter-main'
    Set-Location -LiteralPath $starterProject
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $starterProject 'setup.ps1')
    if ($LASTEXITCODE -ne 0) { throw "Встановлення не завершено. Перегляньте помилку вище; файли залишено в $starterProject" }
} finally {
    if (Test-Path -LiteralPath $starterZip) { Remove-Item -LiteralPath $starterZip -Force }
}
```

Очікуваний результат: `No broken requirements found`, `Imports OK: 31`, `Chromium OK` та `SUCCESS`. Якщо запускали через інший обліковий запис адміністратора, робочий стіл і встановлення належатимуть саме цьому обліковому запису.

Після встановлення перевірити середовище без повторного завантаження пакетів:

```powershell
$starterProject = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Python-Server-Starter\python-server-starter-main'
& "$starterProject\.venv\Scripts\python.exe" "$starterProject\install_packages.py" --check
```

Якщо вже скопіювали проєкт вручну або хочете повторити встановлення після усунення помилки, відкрийте PowerShell у папці, де лежить `setup.ps1`, і виконайте:

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

## Типові проблеми та відновлення

Звірено з офіційною документацією 15.10.2026. Це можливі сценарії, а не перелік помилок, які вже виникли на перевіреному сервері. Діагностику нижче запускайте в папці, де лежить setup.ps1; після завантаження ZIP це Python-Server-Starter\python-server-starter-main.

| Ознака | Ймовірна причина та наступний крок |
| --- | --- |
| Інсталятор повернув 1625 | Встановлення заборонене політикою Windows. Спробуйте дозволений адміністратором підвищений запуск під своїм користувачем; якщо повторюється — перевірте logs і політики з адміністратором. Відсутність ключів DisableMSI не виключає інших обмежень. |
| Running scripts is disabled / PSSecurityException | Політика PowerShell. Подивіться Get-ExecutionPolicy -List. Параметр Bypass у нашій команді стосується процесу і не перекриває доменні MachinePolicy/UserPolicy. |
| Код 1618 / інша інсталяція вже триває | Дочекайтеся завершення іншого інсталятора або Windows Update та повторіть запуск. Код 3010 означає успіх із запитом на перезавантаження, а не помилку. |
| No matching distribution found | Немає відповідного wheel для версії Python/архітектури або пакет недоступний через мережу чи вибраний індекс. Спершу прочитайте попередні рядки pip. Проєкт використовує only-binary:all:, тому пакет лише з вихідним кодом не встановиться. Для іншої minor-версії Python потрібна нова папка середовища. |
| ResolutionImpossible / конфлікт залежностей | Несумісні вимоги пакетів або старі зафіксовані версії. Збережіть lock-файл, перевірте назви конфліктних пакетів. --refresh перераховує версії, але змінює пакети; спершу випробуйте оновлення в окремій копії вихідного проєкту без .venv. |
| SSL: CERTIFICATE_VERIFY_FAILED | Неправильний час сервера, проблеми довіри до сертифіката або корпоративна перевірка HTTPS. Перевірте дату й довірений CA з адміністратором; для pip можна задати PIP_CERT. Не вимикайте перевірку TLS. |
| Timeout, DNS, 403, proxy authentication | Перевірте доступ до GitHub, python.org, PyPI та CDN браузера. HTTP 403 не доводить проблему ключа: завантаження цього публічного проєкту не потребує API-ключа. Проксі налаштовується окремо для PowerShell та інструментів Python. |
| Chromium не завантажився / Executable does not exist | Повторіть встановлення браузера з тієї самої .venv під користувачем, який запускатиме застосунок. Після оновлення Playwright може знадобитися нова версія браузера. |
| Chromium встановився, але не запускається | Перевірте версію ОС, журнал помилки запуску та блокування захисним ПЗ. Поточна документація Playwright указує Windows 11+ або Windows Server 2019+; це не гарантує роботу кожної конфігурації Server Core. |
| Access denied / WinError 5 або файл зайнятий | Перевірте права на папку та чи не працює ваш застосунок із цієї .venv. Закрийте його перед оновленням. Якщо захист заблокував файл, перевірте журнал/карантин з адміністратором замість вимикання захисту. |
| Немає місця / надто довгий шлях | Потрібне місце для Python, пакетів, ZIP, кешу pip і браузера — також у TEMP та LOCALAPPDATA. Використайте короткий локальний шлях, наприклад C:\Apps\PythonStarter. Підтримку довгих шляхів Windows узгоджуйте з адміністратором. |
| python/pip не знайдено або ModuleNotFoundError | Новий PATH може бути доступний лише в новому терміналі; IDE може використовувати інший Python. Запускайте саме .venv\Scripts\python.exe, активація середовища не обов'язкова. |
| Existing .venv belongs to another setup / Incomplete environment | Скрипт захищає стороннє або несумісне середовище. Не видаляйте його навмання: збережіть папку і створіть нову копію проєкту без .venv. Після зміни minor-версії Python старе середовище не перевикористовується. |
| Після перенесення папки або запуску службою все зламалося | .venv прив'язана до інтерпретатора та шляхів; відтворіть її на місці призначення. Кеш Chromium за замовчуванням належить користувачеві. Для служби/планувальника потрібні правильний обліковий запис, абсолютний шлях до Python і доступ до файлів. |
| No official stable x64 installer found | Задана версія відсутня на сторінці Python, формат сторінки змінився або повернувся вміст проксі. Перевірте офіційну сторінку; скрипт не завантажує альтернативний EXE навмання. |
| Installer signature is not a valid ... signature | Не пройшла перевірка підпису або ланцюжка довіри. Перевірте час, мережу й стан довірених сертифікатів; повторіть офіційне завантаження. Не прибирайте перевірку підпису з коду. |

Джерела: [коди Windows Installer](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes), [політики PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies), [Python у Windows](https://docs.python.org/3/using/windows.html), [переносимість venv](https://docs.python.org/3/library/venv.html), [pip: binary wheels](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-only-binary), [конфлікти залежностей](https://pip.pypa.io/en/stable/topics/dependency-resolution/), [сертифікати pip](https://pip.pypa.io/en/stable/topics/https-certificates/), [вимоги Playwright](https://playwright.dev/python/docs/intro#system-requirements), [браузери Playwright](https://playwright.dev/python/docs/browsers).

### Коротка діагностика

Команди читають стан системи. Перевірки Python виконуйте тільки після появи .venv.

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture
$PSVersionTable.PSVersion
Get-ExecutionPolicy -List
Get-Date
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free

# Після створення середовища:
& .\.venv\Scripts\python.exe -c "import sys, struct; print(sys.executable); print(sys.version); print('bits:', struct.calcsize('P') * 8)"
& .\.venv\Scripts\python.exe -m pip --version
& .\.venv\Scripts\python.exe -m pip check
```

Початкова перевірка мережі (відкритий TCP-порт ще не підтверджує успіх HTTPS чи завантаження через проксі):

```powershell
'github.com', 'codeload.github.com', 'www.python.org', 'pypi.org', 'files.pythonhosted.org', 'cdn.playwright.dev' |
    ForEach-Object { Test-NetConnection -ComputerName $_ -Port 443 -InformationLevel Quiet }
```

CDN може перенаправляти на інші домени; точну адресу невдалого завантаження беріть із помилки. Список вище не є повним переліком дозволів для корпоративного firewall.

### Проксі, сертифікати та повільна мережа

Лише якщо мережа організації цього потребує, задайте в поточному PowerShell реальні параметри, отримані від адміністратора. Це приклад, адреса й шляхи нижче не готові налаштування:

```powershell
$env:HTTPS_PROXY = 'http://proxy.example:8080'
$env:PIP_CERT = 'C:\Certificates\company-ca-bundle.pem'
$env:NODE_EXTRA_CA_CERTS = 'C:\Certificates\company-root.pem'
$env:PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT = '120000'
```

PIP_CERT задає довірений набір CA для pip; NODE_EXTRA_CA_CERTS додає CA для завантажувача Playwright. HTTPS_PROXY підтримують pip і Playwright, але це не налаштовує автоматично Invoke-WebRequest у Windows PowerShell 5.1: для нього потрібні системний проксі або погоджені параметри -Proxy/-ProxyUseDefaultCredentials. [pip: проксі](https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server), [PowerShell Invoke-WebRequest](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-5.1).

У setup.ps1 тайм-аути PowerShell задані явно: 60 секунд для сторінки, 300 для EXE; у команді ZIP — 120 секунд. pip запускається з --timeout 60 та --retries 2: зміна PIP_DEFAULT_TIMEOUT не перевизначає цей аргумент. Параметр Playwright вище впливає лише на завантаження браузера.

### Відновлення після збою

Якщо Python і .venv вже створені, а збій стався на пакетах або браузері, після усунення причини повторіть установлення через наявний інтерпретатор. Це не вибиратиме новий Python:

```powershell
& .\.venv\Scripts\python.exe .\install_packages.py
if ($LASTEXITCODE -ne 0) { throw 'Встановлення ще не завершене — перегляньте першу помилку вище.' }
```

Для розширеного набору додайте --profile all. Якщо потрібні тільки бібліотеки без браузера — додайте --skip-browser; це не підтверджує працездатність Chromium.

Для окремого відновлення Chromium та повної перевірки базового набору:

```powershell
$env:PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT = '120000'
& .\.venv\Scripts\python.exe -m playwright install chromium
if ($LASTEXITCODE -ne 0) { throw 'Не вдалося встановити Chromium.' }
& .\.venv\Scripts\python.exe .\install_packages.py --check
if ($LASTEXITCODE -ne 0) { throw 'Перевірка середовища не пройшла.' }
```

Не запускайте два встановлення/оновлення в одну папку одночасно. Пакети встановлюються не як єдина транзакція: після збою частина середовища може змінитися. Старий lock-файл зберігається, але автоматичного відкату пакетів немає. При додаванні бібліотеки до packages.json повторний запуск враховує її разом зі старими pins; несумісність з pins потребує окремого перегляду версій.

Якщо ZIP розпакувався лише частково, команда першого запуску зупиниться на наявній папці. Збережіть цю папку під іншою назвою й повторіть завантаження в нове місце; не накладайте новий архів поверх робочої .venv.

### Що надіслати для допомоги

Версію Windows, результат короткої діагностики, команду запуску та першу помилку з кількома сусідніми рядками. Інсталятор Python пише журнали в logs; повідомлення pip/Playwright виводяться в консоль. Не публікуйте токени, паролі, URL приватних індексів із обліковими даними або повний дамп змінних середовища.

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