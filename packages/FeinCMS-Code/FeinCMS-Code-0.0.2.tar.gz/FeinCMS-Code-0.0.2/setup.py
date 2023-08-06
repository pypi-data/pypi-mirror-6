from setuptools import setup
import feincms_code

setup(
    name='FeinCMS-Code',
    version=feincms_code.__version__,
    packages=['feincms_code'],
    license='MIT',
    description='Pygments formatter content type for FeinCMS.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard@richard.ward.name',
    url='https://github.com/RichardOfWard/feincms-code',
    install_requires=['django', 'feincms', 'feincms-template-content', 'pygments'],
    test_suite='tests',
)
