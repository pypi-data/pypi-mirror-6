This package provides a NIST SP 800-57 compliant Key Management Infrastructure
(KMI).

To get started do::

  $ python bootstrap.py # Must be Python 2.5 or higher
  $ ./bin/buildout     # Depends on successfull compilation of M2Crypto
  $ ./bin/runserver    # or ./bin/paster serve server.ini

The server will come up on port 8080. You can create a new key encrypting key
using::

  $ wget https://localhost:8080/new -O kek.dat --ca-certificate sample.pem

or, if you want a more convenient tool::

  $ ./bin/testclient https://localhost:8080/new -n > kek.dat

The data encryption key can now be retrieved by posting the KEK to another
URL::

  $ wget https://localhost:8080/key --header 'Content-Type: text/plain' --post-file kek.dat -O datakey.dat --ca-certificate sample.pem

or ::

  $ ./bin/testclient https://localhost:8080/new -g kek.dat > datakey.dat

Note: To be compliant, the server must use an encrypted communication channel
of course.  The ``--ca-certificate`` tells wget to trust the sample self-signed
certificate included in the keas.kmi distribution; you'll want to generate a
new SSL certificate for production use.
