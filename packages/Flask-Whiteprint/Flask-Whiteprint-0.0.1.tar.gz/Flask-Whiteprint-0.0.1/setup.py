from distutils.core import setup
from whiteprint import VERSION

setup(
    name='Flask-Whiteprint',
    packages=['whiteprint'],
    version=VERSION,
    description='An enhancement of flask blueprint. ',
    long_description=open('README.rst').read(),
    license='BSD License',
    author='Su Yeol Jeon',
    author_email='devxoul@gmail.com',
    url='https://github.com/devxoul/flask-whiteprint',
    # download_url='https://pypi.python.org/packages/source/' % VERSION,
    keywords=['Flask', 'Whiteprint', 'Blueprint'],
    classifiers=[]
)
