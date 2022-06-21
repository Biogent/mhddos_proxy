TRANSLATIONS = {
    'No working proxies found - stopping the attack': {
        'ua': 'Не знайдено робочих проксі - зупиняємо атаку'
    },
    'Selected': {
        'ua': 'Обрано'
    },
    'targets for the attack': {
        'ua': 'цілей для атаки'
    },
    'Target': {
        'ua': 'Ціль'
    },
    'Port': {
        'ua': 'Порт'
    },
    'Method': {
        'ua': 'Метод'
    },
    'Packets': {
        'ua': 'Пакети'
    },
    'Traffic': {
        'ua': 'Трафік'
    },
    'Total': {
        'ua': 'Усього'
    },
    'Loaded config for': {
        'ua': 'Завантажено конфіг на'
    },
    'Targets loading failed': {
        'ua': 'Завантаження цілей завершилося помилкою:'
    },
    'No targets specified for the attack': {
        'ua': 'Не вказано жодної цілі для атаки'
    },
    'Launching the attack...': {
        'ua': 'Запускаємо атаку...'
    },
    'Empty config loaded - the previous one will be used': {
        'ua': 'Завантажено порожній конфіг - буде використано попередній'
    },
    'Failed to (re)load targets config:': {
        'ua': 'Не вдалося (пере)завантажити конфіг цілей:'
    },
    'Failed to reload proxy list - the previous one will be used': {
        'ua': 'Не вдалося перезавантажити список проксі - буде використано попередній'
    },
    'A new version is available, update is recommended': {
        'ua': 'Доступна нова версія, рекомендуємо оновити'
    },
    'The number of threads has been reduced to': {
        'ua': 'Кількість потоків зменшено до'
    },
    'due to the limitations of your system': {
        'ua': 'через обмеження вашої системи'
    },
    'Shutting down...': {
        'ua': 'Завершуємо роботу...'
    },
    'The number of copies is automatically reduced to': {
        'ua': 'Кількість копій автоматично зменшена до'
    },
    'Threads': {
        'ua': 'Потоків'
    },
    'Using only proxies': {
        'ua': 'Атака тільки через проксі'
    },
    'Using both proxies and your IP/VPN': {
        'ua': 'Атака через проксі та ваш IP/VPN'
    },
    'Using only your IP/VPN (no proxies)': {
        'ua': 'Атака тільки через ваш IP/VPN (без проксі)'
    },
    'Delay in execution of operations detected': {
        'ua': 'Зафіксована затримка у виконанні операцій'
    },
    'the attack continues, but we recommend reducing the workload': {
        'ua': 'атака продовжується, але рекомендуємо зменшити значення навантаження'
    },
    'Workload (number of threads)': {
        'ua': 'Навантаження (кількість потоків)'
    },
    'use flag `-t XXXX`, default is': {
        'ua': 'параметр `-t XXXX`, за замовчуванням -'
    },
    'Complete documentation': {
        'ua': 'Повна документація'
    },
    'Consider adding your IP/VPN to the attack - use flag `--vpn`': {
        'ua': 'Щоб використовувати ваш IP/VPN на додачу до проксі: параметр `--vpn`'
    },
    'Instead of high `-t` value consider using': {
        'ua': 'Замість високого значення `-t` краще використати'
    },
    'The `--debug` option is deprecated to avoid negative impact on performance': {
        'ua': 'Параметр `--debug` не підтримується через негативний вплив на продуктивність'
    },
    'Try running with automatic updates: ': {
        'ua': 'Радимо запускати скрипт з автоматичним оновленням: '
    },
    '`uvloop` activated successfully': {
        'ua': '`uvloop` успішно активовано'
    },
    '(increased network efficiency)': {
        'ua': '(підвищенна ефективність роботи з мережею)'
    },
    'targets': {
        'ua': 'цілей'
    },
    "is not available and won't be attacked": {
        'ua': 'не доступна і не буде атакована'
    },
    'Capacity': {
        'ua': 'Потужність'
    },
    'Connections': {
        'ua': "З'єднань"
    },
    'Concurrency was reduced to': {
        'ua': 'Кількість потоків на одну копію було зменшено до'
    },
    'per copy to match the size of available port range': {
        'ua': '(згідно з максимальною кількістю портів)'
    },
}

LANGUAGES = ['ua', 'en']
DEFAULT_LANGUAGE = LANGUAGES[0]


class _Translations:
    def __init__(self):
        self.language = None
        self.translations = TRANSLATIONS

    def set_language(self, language: str):
        assert language in LANGUAGES
        self.language = language

    def translate(self, key: str) -> str:
        try:
            return self.translations[key][self.language]
        except KeyError:
            return key


_inst = _Translations()

set_language = _inst.set_language
translate = _inst.translate
