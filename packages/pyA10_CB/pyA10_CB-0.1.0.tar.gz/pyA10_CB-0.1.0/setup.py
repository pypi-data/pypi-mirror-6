from distutils.core import setup, Extension


setup(
    name                = 'pyA10_CB',
    version             = '0.1.0',
    author              = 'Markus Sigg',
    author_email        = 'dev.siggie@gmail.com',
    url                 = 'http://linux-sunxi.org',
    license             = 'MIT',
    description         = 'Control GPIOs on Cubieboard A10.',
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
    ext_modules         = [Extension('A10_GPIO', ['source/gpio_lib.c', 'source/pyA10.c'])],
    package_dir={'': 'source'},
    packages=[''],
  
                            
)
