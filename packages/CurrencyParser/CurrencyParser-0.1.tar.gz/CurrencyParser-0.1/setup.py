from distutils.core import setup

setup(
        name='CurrencyParser',
        version='0.1',
        author='Alex Sidorov',
        author_email='alex.n.sidorov@gmail.com',
        packages=(
            'currencyparser',
            'currencyparser.test',
            ),
        scripts=(
            ),
        url='http://pypi.python.org/pypi/CurrencyParser/',
        license='LICENSE',
        description='Smart currency and its amount parser',
        long_description=open('README.txt').read(),
        install_requires=(
            ),
        )
