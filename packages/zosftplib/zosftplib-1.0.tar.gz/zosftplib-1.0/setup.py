from setuptools import setup, find_packages
import re

RST='zosftplib.rst'
open("README.rst","w").write(re.sub(r'\.\.\s*sourcecode\s*\:\:\s*\w*','::',open(RST).read()))

setup(name="zosftplib",
      py_modules=['zosftplib'],
      version="1.0",
      author='Denis Wallerich',
      author_email='denis.wallerich@datim.fr',
      url = "http://www.datim.fr",
      include_package_data=True,
      license='BSD',
      description = 'z/OS Mainframe ftplib subclass',
      long_description=open('README.rst').read(),
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Hardware :: Mainframes",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: Software Development :: Libraries",
        "Intended Audience ::  Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",]
      )

