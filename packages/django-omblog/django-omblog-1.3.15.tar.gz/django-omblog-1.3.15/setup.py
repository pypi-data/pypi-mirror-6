import os
from distutils.core import setup
from omblog import VERSION

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name='django-omblog',
    version=VERSION,
    license = 'BSD 3 Clause',
    description='A speedy django blog',
    url='https://github.com/jamiecurle/django-omblog',
    author='Jamie Curle',
    author_email='jamie@curle.io',
    package_data = {
        'omblog' : [
            'templates/omblog/*.html',
            'templates/search/indexes/omblog/*.txt',
            'static/omblog/css/*',
            'static/omblog/fonts/*',
            'static/omblog/js/*',
            'static/omblog/img/*',
        ]
    },
    packages=[
        'omblog',
        'omblog.templatetags',
        'omblog.tests',
        'omblog.migrations',
    ],
    install_requires = [
        'beautifulsoup4',
        'Pillow',
        'pygments',
        'markdown2'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',]
)
