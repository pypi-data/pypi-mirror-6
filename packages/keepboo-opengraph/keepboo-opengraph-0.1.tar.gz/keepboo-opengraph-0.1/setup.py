from distutils.core import setup

setup(
    name='keepboo-opengraph',
    version='0.1',
    packages=['keepboo_opengraph'],
    url='https://github.com/KEEPBOO/keepboo',
    license='',
    author='Oleg Stasula',
    author_email='oleg.stasula@gmail.com',
    description='Open Graph parser used on keepboo.com',
    long_description=open("README.txt").read() + "\n",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    keywords='opengraph keepboo parser',
    install_requires=[
        'beautifulsoup4'
    ],
)
