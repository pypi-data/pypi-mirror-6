from setuptools import setup, find_packages
setup(
    name='memorycoin-python',
    version='0.1',
    description='Friendly Memorycoin JSON-RPC API binding for Python',
    long_description='This package allows performing commands such as listing the current balance'
    ' and sending coins to the Satoshi (original) client from Python. The communication with the'
    ' client happens over JSON-RPC.',
    maintainer='Emre Yilmaz',
    maintainer_email='mail@emreyilmaz.me',
    url='http://github.com/emre',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Office/Business :: Financial'
    ],
    packages=find_packages("src"),
    package_dir={'': 'src'}
)
