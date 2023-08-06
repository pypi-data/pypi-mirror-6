=======
CHANGES
=======

2.1.1 (2014-04-07)
------------------

- Bug: FileDataGenerator used the full filename to generate the random seed.
  That is definitely going to break consistency/tests on someone else's system.


2.1.0 (2013-03-15)
------------------

- Switched code base to use ``random2``, so that Python 2 and 3 have the same
  output. No need for running different test files now.

- Simplified and unified test setup.


2.0.1 (2013-02-12)
------------------

- Updated manifest to include buildout and tox configuration files.

- Updated Trove classifiers.

- Renamed text files from *.txt to *.rst,s o Github renders them nicely.


2.0.0 (2013-02-06)
------------------

- Feature: Support for Python 3.

- Bug: Make sure that all files are closed properly.

- Bug: When generating a username, make sure it does not include any special
  characters passed through by the first or lastname, for example "O'Dorothy".

1.0.0 (2013-02-06)
------------------

- Feature: Added tests for all data generators.

- Feature: Added an ID data generator that can generate all sorts of IDs that
  could occur in systems.

- Feature: To properly support Windows, ``consistent_hash()`` returns an
  integer.

- Bug: The IPv4 generator ignored the seed making the generator "unstable".

0.0.3 (2008-12-03)
------------------

- Refined the seed generation further: zlib.crc32() in 32 bit Python can
  generate negative hashes, while 64 bit Python does not.  Enforced
  positive hashes.

- Began a test suite.


0.0.2 (2008-12-02)
------------------

- Use the crc32 function to hash random seeds so that the
  same random sequences are generated on both 32 bit and 64 bit
  builds of Python.


0.0.1 (2008-02-14)
------------------

- Initial Release
