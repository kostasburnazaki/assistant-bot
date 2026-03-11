from setuptools import setup, find_packages

setup(
    name='assistant-bot',
    version='0.1',
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
      Опис бота
      ''',
)
