from setuptools import setup


setup(
    name='cloud_elements_test_framework',
    version='0.0.7',
    author='Josh Wyse',
    author_email='josh@cloud-elements.com',
    packages=['cloud_elements_test_framework'],
    keywords='cloud elements',
    description='Cloud Elements Testing Framework for Python',
    long_description='Cloud Elements Integration Testing Framework for Python',
    install_requires=[
        'argparse',
        'cloud_elements'
    ],
    url='https://github.com/cloud-elements/elements-test-framework'
)
