from setuptools import setup

setup(
    name = 'comicslicer',
    packages = ['comicslicer'],
    version = '0.0.1',
    description = 'slices a comic',
    author='Arne Hilmann',
    author_email='arne.hilmann@t-online.de',
    url='https://github.com/arnehilmann/comicslicer',
    install_requires=["numpy"],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion'
    ]
)
