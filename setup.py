from setuptools import setup

APP = ['check_sites.py']  # замени на своё имя скрипта
OPTIONS = {
    'argv_emulation': True,
    'packages': ['requests'],  # и любые другие зависимости
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
