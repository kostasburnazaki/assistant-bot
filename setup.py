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
        'markdown-it-py==4.0.0',
        'mdurl==0.1.2',
        'Pygments==2.19.2',
        'rich==14.3.3',
    ],
    author='One-team',
    description='''
        Бот для контактів. Має функції додавання, збереження та редагування даних та нотаток контакта.
      ''',
)
