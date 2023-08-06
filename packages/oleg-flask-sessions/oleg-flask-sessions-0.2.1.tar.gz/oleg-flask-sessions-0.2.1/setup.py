from setuptools import setup

setup(
    author='Quinlan Pfiffer',
    author_email='qpfiffer@gmail.com',
    url='https://github.com/infoforcefeed/OlegDBFlaskSessions',
    name='oleg-flask-sessions',
    description='Oleg DB backed sessions for Flask',
    version='0.2.1',
    license='BSD',
    keywords='OlegDB, Flask',
    packages=['olegsessions'],
    zip_safe=False,
    install_requires = [
        "werkzeug",
        "msgpack-python",
        "flask"
    ]
)
