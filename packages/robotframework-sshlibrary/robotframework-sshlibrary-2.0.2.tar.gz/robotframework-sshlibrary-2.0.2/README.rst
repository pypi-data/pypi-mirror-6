SSHLibrary for Robot Framework
==============================

Introduction
------------

SSHLibrary is a Robot Framework (http://robotframework.org) test library for
testing SSH and SFTP.

The library has the following main usages:
- Executing commands on remote, either with blocking or non-blocking behaviour.
- Writing and reading in an interactive session.
- Transferring files and directories over SFTP.
- Ensuring that files or directories exist on remote.


License
-------

SSHLibrary is licensed under Apache License 2.0.

See LICENSE.txt for details.


Installation
------------

Install from Python Package Index:
pip install robotframework-sshlibrary

The installation is documented at
http://code.google.com/p/robotframework-sshlibrary/wiki/InstallationInstructions.

For general information about using test libraries with Robot Framework, see
http://robotframework.googlecode.com/hg/doc/userguide/RobotFrameworkUserGuide.html#using-test-libraries.


Documentation
-------------

The documentation and examples can be found at 'doc/SSHLibrary.html' or at
https://code.google.com/p/robotframework-sshlibrary/wiki/KeywordDocumentation.


Directory Layout
----------------

atest/
    Acceptance tests. Naturally using Robot Framework.

doc/
    SSHLibrary documentation.

lib/
    Contains Trilead SSH library JAR distribution which must be in CLASSPATH
    when executing tests with Jython.

src/
    SSHLibrary source code.

utests/
    Unit tests.


Running the Acceptance Tests
----------------------------

Running the acceptance tests requires some configuration which is explained at
https://code.google.com/p/robotframework-sshlibrary/wiki/RunningLibraryAcceptanceTests
