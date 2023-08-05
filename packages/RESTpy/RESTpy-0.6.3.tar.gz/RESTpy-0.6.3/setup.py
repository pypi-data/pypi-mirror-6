from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='RESTpy',
    version='0.6.3',
    url='https://github.com/kevinconway/rest.py',
    license=license,
    description='Werkzeug extensions for building RESTful services.',
    author='Kevin Conway',
    author_email='kevinjacobconway@gmail.com',
    long_description=readme,
    classifiers=[],
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    install_requires=[
        'Werkzeug'
    ]
)
