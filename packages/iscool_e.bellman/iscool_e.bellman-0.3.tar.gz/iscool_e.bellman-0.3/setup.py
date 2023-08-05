from setuptools import setup, find_packages, Extension
import sys
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.3'

install_requires = [
    'requests',
]

# make extensions
def extension_maker():
    extensions = []

    def loop(directory, module=None):
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            name = module + "." + file if module else file
            if os.path.isfile(path) and path.endswith(".c"):
                extensions.append(
                    Extension(
                        name=name[:-2],
                        sources=[path],
                        include_dirs=['src', "."],
                    )
                )
            elif os.path.isdir(path):
                loop(path, name)

    loop('src/iscool_e', 'iscool_e')
    return extensions


setup(
    name='iscool_e.bellman',
    version=version,
    description=str(
        'A library to support the REST API of'
        'mobile push notification server Pushd'
    ),
    long_description=README + '\n\n' + NEWS,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    keywords='pushd sdk api python',
    author='Thomas Ferreira',
    author_email='thomas.ferreira@iscool-e.com',
    url='https://github.com/tferreira/bellman-sdk',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['iscool_e'],
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    ext_modules=extension_maker()
)
