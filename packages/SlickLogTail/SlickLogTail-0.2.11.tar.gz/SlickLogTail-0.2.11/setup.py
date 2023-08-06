from distutils.core import setup

setup(
    name='SlickLogTail',
    version='0.2.11',
    author='Torindo Nesci',
    author_email='torindo.nesci@slicklog.com',
    packages=['slicklogtail'],
    scripts=[],
    entry_points={
        'console_scripts': ['slicklogtail=slicklogtail.command_line:main'],
    },
    url='http://slicklog.com/',
    license='LICENSE.txt',
    description='SlickLog.com Python SlickLogTail.',
    long_description=open('README.txt').read(),
    install_requires=[
        "SlickLogHandler >= 0.2.8"
    ],
)
