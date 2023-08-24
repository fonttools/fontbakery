Source Code Contributor Guide
=============================

Contributions to the Font Bakery source code are welcomed! Please read
and follow the instructions in :doc:`contrib-getting-started` and then 
use the instructions below to set up a source code development environment.

.. important:: 

   Please note that the required dependencies are different for 
   documentation development and source code development.  Please 
   see the :doc:`doc-contrib-guide` if you are attempting to 
   improve our docs!


Create a Font Bakery Development Environment
--------------------------------------------

You must have a Python 3 interpreter and the ``pip`` Python package
manager installed on your system to participate in Font Bakery
development.

Clone the Font Bakery Source Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pull the source repository with the following command:

::

   $ git clone https://github.com/fonttools/fontbakery.git

and navigate to the root of the repository with:

::

   $ cd fontbakery

Create a Python Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Execute the following command in the root of the Font Bakery source
repository to create a Python virtual environment for development and
testing:

::

   $ python3 -m venv fontbakery-venv

Activate Virtual Environment and Install Font Bakery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Activate the Python virtual environment with:

Unix platforms
^^^^^^^^^^^^^^

::

   $ source fontbakery-venv/bin/activate

Windows platform
^^^^^^^^^^^^^^^^

::

   $ fonttools-venv\Scripts\activate.bat


Next, install the Font Bakery source in editable mode with:

::

   $ pip install -e .


.. important:: 

   Please note that there are optional non-Python dependencies that must be installed to 
   execute some features in the Font Bakery project.  Please see the 
   :doc:`../user/installation/index` for additional details.

You are now ready to modify the Font Bakery source files and test your changes.

When your work is complete, deactivate the virtual environment with the following command::

   $ deactivate  

Custom Font Bakery Profiles
---------------------------------

Please see :doc:`writing-profiles` for instructions on how to
write custom Font Bakery profiles.

Source Code Testing
-------------------

Font Bakery provides over 2 hundred checks for fonts and families.

It also contains a set of code tests to assure the quality of the Font Bakery
suite of checks. We aim to reach 100% test coverage.


In order to run the tests you need to have the ``pytest`` dependency installed.

Install ``pytest``
~~~~~~~~~~~~~~~

Install ``pytest`` in your virtual environment with:

::

   $ pip install pytest


Execute Source Code Test Suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the following command in the root of the source repository to
execute the Font Bakery test suite:

::

   $ pytest tests


Propose Source Code Changes
---------------------------

All proposals for source code modifications, including submissions by
project members, require a review process. We use GitHub pull requests
for this purpose. Consult `GitHub
Help <https://help.github.com/articles/about-pull-requests/>`__ for more
information on using pull requests to submit your changes for review.

The test suite that you execute locally with ``pytest`` is executed by 
the Github Actions automatically when you submit a pull request to the
repository. Please add new tests that cover your source changes with all
proposals. Pull requests cannot be merged if any test fails as a result
of your modifications.

.. important:: Please submit tests that cover all source code changes in your pull request!

The build logs can be viewed at
https://github.com/fonttools/fontbakery/actions


Community Guidelines
--------------------

This project follows `Google's Open Source Community Guidelines <https://opensource.google.com/conduct/>`_ and 
the Font Bakery `Code of Conduct <https://github.com/fonttools/fontbakery/blob/main/CODE_OF_CONDUCT.md>`_.


License
-------

The source code is licensed under the `Apache v2.0
License <https://github.com/fonttools/fontbakery/blob/main/LICENSE.txt>`__.
