from distutils.core import setup

setup(
    name='Blackjack',
    version='1.0',
    description='Blackjack CLI interactive game and simulator.',
    author='Ellis Andrews',
    packages=['blackjack'],
    install_requires=['matplotlib', 'pandas', 'tqdm']
)
