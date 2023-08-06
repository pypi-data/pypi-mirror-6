from distutils.core import setup

setup(
    name = 'dataview',
    packages = ['dataview'],
    version = '1.0.2',
    description = 'A module that allows you to create views of your sequences or its slices',
        author = 'Dmitriy Kirichenko',
        author_email = 'damamaty@gmail.com',
        url = 'https://github.com/damamaty/dataview',
        download_url = 'https://github.com/damamaty/dataview/tarball/v1.0.1',
        keywords = [],
        classifiers=[
            'Environment :: Console',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.3',
        ],
        long_description=open('README.rst', 'r').read(),
        license=open('LICENSE', 'r').read(),
)