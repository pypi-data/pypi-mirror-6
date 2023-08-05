from setuptools import setup
import pspecs

if __name__ == "__main__":
    setup(
        name='pspecs',
        description='easy, readable python test specifications inspired by rspec',
        version=pspecs.__version__,
        license='MIT',
        author='Catalin Costache',
        author_email='catacgc@gmail.com',
        url='http://github.com/catacgc/python-specs/',
        py_modules=['pspecs', 'pytest_specs', 'nose_specs'],
        entry_points={
            'pytest11': ['specs = pytest_specs'],
            'nose.plugins.0.10': ['specs = nose_specs:SpecsPlugin']
        },
        install_requires=['pytest>=2.4.2', 'nose>=1.3.0'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Environment :: Console',
            'Programming Language :: Python',
            'Topic :: Software Development :: Documentation',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
            'Topic :: Utilities',
            ]
        )