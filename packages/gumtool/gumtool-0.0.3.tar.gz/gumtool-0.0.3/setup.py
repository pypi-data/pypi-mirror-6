from setuptools import setup, find_packages

setup(
    name='gumtool',
    version='0.0.3',
    description=(
        "A simple collection of tools that make running Gnome (3.10+) "
        "Ubuntu (14.04+) a little easier, especially on high-dpi hardware "
        "like the Retina MacbookPro."),
    author='Jose A. Idar',
    author_email='jose.idar@gmail.com',
    url='blog.thatjoseguy.com',
    packages=find_packages(),
    install_requires=['argh'],
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points = {
        'console_scripts':
        ['gumtool = gumtool.cli:entry_point']}
    )
