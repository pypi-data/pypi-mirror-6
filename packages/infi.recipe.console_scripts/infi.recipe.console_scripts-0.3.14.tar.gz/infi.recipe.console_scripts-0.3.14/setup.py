
SETUP_INFO = dict(
    name = 'infi.recipe.console_scripts',
    version = '0.3.14',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'https://github.com/Infinidat/infi.recipe.console_scripts',
    license = 'PSF',
    description = """buildout recipe for generating better console and gui script for entry points""",
    long_description = """buildout recipe for generating better console and gui script for entry points""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['infi.pyutils',
'setuptools',
'z3c.recipe.scripts',
'zc.buildout',
'zc.recipe.egg'],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': ['msvcp90.dll-x86', 'embed-x86.exe', 'embed-gui-x86.exe', 'msvcp90.dll-x64', 'embed-gui-x64.exe', 'embed-x64.exe', 'msvcr90.dll-x86', 'Microsoft.VC90.CRT.manifest-x86', 'msvcm90.dll-x64', 'msvcm90.dll-x86', 'Microsoft.VC90.CRT.manifest-x64', 'msvcr90.dll-x64']},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': ['console-script-test = infi.recipe.console_scripts:nothing', 'replace_gui_script = infi.recipe.console_scripts.windows:replace_gui_script', 'replace_console_script = infi.recipe.console_scripts.windows:replace_console_script'],
        'gui_scripts': ['gui-script-test = infi.recipe.console_scripts:nothing'],
        'zc.buildout': ['default = infi.recipe.console_scripts:Scripts',
                        'script = infi.recipe.console_scripts:Scripts',
                        'scripts = infi.recipe.console_scripts:Scripts',
                        'gui_script = infi.recipe.console_scripts:GuiScripts',
                        'gui_scripts = infi.recipe.console_scripts:GuiScripts',]
        }
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

