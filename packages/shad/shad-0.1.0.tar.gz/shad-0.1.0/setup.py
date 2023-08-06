try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'shad',
]

requires = ['requests>=1.2.0']

setup(
    name='shad',
    version='0.1.0',
    description='Generic restful api -> Python function call adaptor',
    long_description=open('README.md').read(),
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='https://bitbucket.org/amjoconn/shad',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
)
