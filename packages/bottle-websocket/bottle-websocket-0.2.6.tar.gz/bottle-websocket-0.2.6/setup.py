from setuptools import setup

setup(
    name='bottle-websocket',
    version='0.2.6',
    license='MIT',
    url='https://github.com/zeekay/bottle-websocket',
    author='Zach Kelling',
    author_email='zk@monoid.io',
    packages=['bottle_websocket',],
    package_data={'': ['README.md']},
    description='WebSockets for bottle',
    long_description=open('README.md'),
    install_requires=['bottle', 'gevent-websocket'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='bottle websockets',
)
