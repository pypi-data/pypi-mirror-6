
from distutils.core import setup

setup(
    name = 'simple-crypt',
    keywords = ['aes', 'encrypt', 'decrypt', 'encryption', 'decryption', 'pbkdf2', 'hmac', 'secure', 'crypto', 'cryptography'],
    url = 'https://github.com/andrewcooke/simple-crypt',
    requires = 'pycrypto',
    install_requires = ['pycrypto'],
    packages = ['simplecrypt'],
    package_dir = {'': 'src'},
    version = '2.0.1',
    description = 'Simple, secure encryption and decryption for Python 2.7 and 3',
    author = 'Andrew Cooke',
    author_email = 'andrew@acooke.org',
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: Public Domain',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Security',
                   'Topic :: Security :: Cryptography',
                   'Topic :: Software Development'],
    long_description = '''
What Does Simple Crypt Do?
--------------------------

Simple Crypt encrypts and decrypts data.  It has two functions, ``encrypt``
and ``decrypt``::

    from simplecrypt import encrypt, decrypt
    ciphertext = encrypt('password', plaintext)
    plaintext = decrypt('password', ciphertext)

That's it.  You can see the implementation on
`github <https://github.com/andrewcooke/simple-crypt/blob/master/src/simplecrypt/__init__.py>`_.

Why Should I Use Simple Crypt?
------------------------------

* It uses standard, well-known algorithms, closely following the
  recommendations `here <http://www.daemonology.net/blog/2009-06-11-cryptographic-right-answers.html>`_.

* The established, efficient `pycrypto <https://www.dlitz.net/software/pycrypto>`_
  library provides the algorithm implementations (the cipher used is AES256).

* It includes a check (an HMAC with SHA256) to warn when ciphertext data are
  modified.

* It tries to make things as secure as possible when poor quality passwords
  are used (PBKDF2 with SHA256, a 128 bit salt, and 10,000 rounds).  But that
  doesn't mean you should use a poor password!

* Using a library, rather than writing your own code, means that we have less
  solutions to the same problem.  That means more chance of finding bugs, which
  means more reliable, more secure code.

* If simple-crypt does have a bug, the use of a header in the ciphertext data
  will help support an upgrade path (I can't promise full backwards support,
  because any solution will depend on the attack, but at least the needed
  information is present).

What Else Should I Know?
------------------------

* You must also install ``pycrypto``.

* In Python 3 the outputs from ``encrypt`` and ``decrypt`` are ``bytes``.
  If you started with string input then you can convert the output from
  ``decrypt`` using ``.decode('utf8')``.

::

    mystring = decrypt('password', ciphertext).decode('utf8')

* (c) 2012 Andrew Cooke, andrew@acooke.org;
  2013 `d10n <https://github.com/d10n>`_, david@bitinvert.com.
  Released into the public domain for any use, but with absolutely no warranty.
    '''
)
