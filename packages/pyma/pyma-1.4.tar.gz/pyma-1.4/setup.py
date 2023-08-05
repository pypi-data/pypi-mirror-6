from setuptools import setup

setup(name='pyma',
    version='1.4',
    description='A simple library for executing moving average function on a dataset',
    long_description="This library provide simple moving average function, namely, Simple Moving Average, Exponential Moving Average and N day Exponential Moving Average.",
    Keywords="exponential moving average data ema ma ewma",
    url='https://bitbucket.org/aideaucegep/pyma',
    author='Pierre-Yves Mathieu',
    author_email='github@pywebdesign.net',
    license='MIT',
    packages=['pyma'],
    include_package_data=True,
    zip_safe=False)