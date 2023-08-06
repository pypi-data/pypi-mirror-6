from distutils.core import setup, Extension


setup(
    name                = 'pyA13',
    version             = '0.1.13',
    author              = 'Stefan Mavrodiev',
    author_email        = 'support@olimex.com',
    url                 = 'https://www.olimex.com/',
    license             = 'MIT',
    description         = 'Control GPIOs on OLinuXino-A13.',
    long_description    = open('README.txt').read() + open('CHANGES.txt').read(),
    classifiers         = [ 'Development Status :: 3 - Alpha',
                            'Environment :: Console',
                            'Intended Audience :: Developers',
                            'Intended Audience :: Education',
                            'License :: OSI Approved :: MIT License',
                            'Operating System :: POSIX :: Linux',
                            'Programming Language :: Python',
                            'Topic :: Home Automation',
                            'Topic :: Software Development :: Embedded Systems'
          ],
    ext_modules         = [Extension('A13_GPIO', ['source/gpio_lib.c', 'source/pyA13.c'])],
    package_dir={'': 'source'},
    packages=[''],
  
                            
)
