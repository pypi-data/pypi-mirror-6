from setuptools import setup

setup(
    name='ail',
    version=__import__('ail').__version__,
    description='abstract interaction layer',
    url='https://github.com/jeandesmorts/ail',
    license='WTFPLv2',
    author='jdmorts',
    author_email='jean.des.morts@gmail.com',
    setup_requires=['nose>=1.0'],
    include_package_data=True,
    packages=['ail', 'ail.platforms', 'ail.services', 'ail.tests',
              'ail.platforms.cloudstream', 'ail.platforms.equallogic',
              'ail.platforms.linux'],
    long_description="""ail is a generalized framework for interacting with...\
    well, stuff. It is sometimes better to ail than fail.""",
    classifiers=[
        'License :: Public Domain',  # OSI Rejected :: WTFPLv2
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',  # Drunk automata
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    keywords='automation',
    install_requires=['setuptools'],
)
