""" package setup
"""
from os.path import join, dirname

from pip.req import parse_requirements
from setuptools import setup, find_packages


def read_requirements():
    """ utility function to read in and parse requirements.txt """
    install_reqs = parse_requirements('requirements.txt')
    return [str(ir.req) for ir in install_reqs]


setup(
    name='blogtopoid',
    version='0.0.1a',
    author='chris',
    author_email='cg@zknt.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    url='https://github.com/hansenerd/blogtopoid/',
    license='MIT',
    description='simple blog generator',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',

    ],
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': ['blogtopoid = blogtopoid:main'],
    },
    setup_requires=["pip", "setuptools_git >= 0.3"],
    exclude_package_data={'': ['.gitignore']},
    test_suite="blogtopoid.test",
)
