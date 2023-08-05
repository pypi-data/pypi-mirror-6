from distutils.core import setup

setup(
    name='PostmanProxy',
    version='0.1.5',
    author='Abhinav Asthana',
    author_email='abhinav@rickreation.com',
    packages=['postmanproxy', 'postmanproxy.postman'],
    url='http://pypi.python.org/pypi/PostmanProxy/',
    license='LICENSE.txt',
    description='An HTTP proxy for doing some cool things with Postman',
    long_description=open('README.txt').read(),
    entry_points={
        'console_scripts': [
            'pmproxy = postmanproxy.main:main',
        ]
    },
    install_requires=[
        "mitmproxy >= 0.9.2",
        "Werkzeug >= 0.9.4"
    ],
)