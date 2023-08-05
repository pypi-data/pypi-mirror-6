from setuptools import setup, find_packages
setup(
    name = "HexClient",
    version = "0.1.2",
    #packages = find_packages(),
    py_modules = ['hex_client', 'hex_connection', 'spellbook'],
    scripts = ['hex_client'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        'requests',
        'sphinx'
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst']
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Chris Proctor",
    author_email = "chris.proctor@gmail.com",
    description = "A client for casting spells on the hex",
    license = "MIT",
    keywords = "",
    url = "http://mrproctor.net",   # project home page, if any

)
