from distutils.core import setup

setup(
    name = 'google_play_rank',
    packages = ['google_play_rank'],
    version = '0.1.2',
    description = 'Input a package name, then find the ranking for you.',
    author = 'davidyen1124',
    author_email = 'davidyen1124@gmail.com',
    url = 'https://github.com/davidyen1124/google_play_rank',
    keywords = ['google play', 'ranking', 'android', 'package name'],
    install_requires = [
        'requests',
        'BeautifulSoup4',
    ]
)
