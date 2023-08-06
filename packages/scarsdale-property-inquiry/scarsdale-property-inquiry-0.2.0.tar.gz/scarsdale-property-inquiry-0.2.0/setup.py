from distutils.core import setup

setup(name='scarsdale-property-inquiry',
    author='Thomas Levine',
    author_email='_@thomaslevine.com',
    description='Inquire about Scarsdale properties',
    url='https://github.com/tlevine/scarsdale-property-inquiry.git',
    classifiers=[
        'Intended Audience :: Developers',
    ],
    packages=['scarsdale_property_inquiry'],
    scripts=['bin/scarsdale-property-inquiry'],
    install_requires = ['requests','randua','lxml','pickle_warehouse','randomsleep','dataset'],
    tests_require = ['nose'],
    version='0.2.0',
    license='AGPL',
)
