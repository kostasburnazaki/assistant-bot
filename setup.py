from setuptools import setup, find_packages

setup(
    name='assistant-bot',
    version='0.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'assistant=cli.bot:main',
        ],
    },
    install_requires=[
        # тут залежності, якщо є
    ],
    author='One-team',
    description='''
        Бот для контактів. Має функції додавання, збереження та редагування даних та нотаток контакта.
      ''',
)
