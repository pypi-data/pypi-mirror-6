from distutils.core import setup
try:
    import py2exe
except ImportError:
    py2exe = None

setup(name='log-dump',
      version='0.1.1',
      scripts=['log_dump.py', ],
      author='Gabriel Abdalla Cavalcante',
      author_email='gabriel.cavalcante88@gmail.com',
      data_files=['README.md',],
      description = ("""Log-Dump is a Python script to dump
		      and generate all Windows Logon Errors,
		 primary the 4625 and 4771 events on
		Windows 2008 / 2012 Servers and
		529 on Windows 2003 Servers."""),
      url='https://github.com/gcavalcante8808',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: System :: Systems Administration',
      ]
)
