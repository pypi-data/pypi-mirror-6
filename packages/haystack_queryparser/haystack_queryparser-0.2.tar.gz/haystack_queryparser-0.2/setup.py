from distutils.core import setup

setup(name='haystack_queryparser',
      version='0.2',
      description='A search query parser that works in conjunction with haystack',
      author='Vignesh Sarma K',
      author_email='vignesh@recruiterbox.com',
      url='https://github.com/recruiterbox/haystack-queryparser',
      download_url='https://github.com/recruiterbox/haystack-queryparser/tarball/0.2',
      classifiers = [
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      ],
      keywords = ["parsing", "query", "search"],
      packages = ['haystack_queryparser'],
)
