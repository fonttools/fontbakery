Documentation Contributor Guide
===============================

Contributions to the Font Bakery documentation are welcomed! Please read
and follow the instructions below to improve our documentation.

.. important:: 

   Please note that the required dependencies are different for 
   documentation development and source code development.  Please 
   see the :doc:`source-contrib-guide` if you are attempting to 
   modify the Python source code!


Create a Font Bakery Development Environment
--------------------------------------------

You must have a Python 3 interpreter and the ``pip`` Python package
manager installed on your system to participate in Font Bakery
documentation development.

Clone the Font Bakery Source Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pull the source repository with the following command:

::

   $ git clone https://github.com/googlefonts/fontbakery.git

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

   $ pip install -e ".[docs]"


.. important:: Please note that this intall step differs from that in the :doc:`source-contrib-guide`.
   Make sure that you include ``[docs]`` in the argument to install additional dependencies that are 
   required to build the documentation.  This argument may need to be quoted on the command line as
   demonstrated above.

You are now ready to modify the Font Bakery documentation files and test your changes.

When your work is complete, deactivate the virtual environment with the following command::

   $ deactivate  


Documentation Style Guide
-------------------------

We follow the `Google Python Style Guide docstring format <https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings>`_.  Documentation with appropriately
formatted Python source file docstrings are automatically parsed into formatted documentation files that are displayed on Read The Docs. Please read the Style Guide
and follow this format for documentation that you contribute to the Font Bakery project.


Build Local Documentation
-------------------------

Navigate to the ``docs`` directory of the Font Bakery repository and use one of the two following commands:

Build with ``make``
~~~~~~~~~~~~~~~~~~~

If ``make`` is installed on your system, use::

   $ make html


Build without ``make``
~~~~~~~~~~~~~~~~~~~~~~

If ``make`` is not installed on your system, use::

   $ sphinx-build -b html source _build 


Review Local Documentation
--------------------------

The compiled files are found on the path ``docs/_build/html``.  Open the ``index.html`` file in your browser
to view your edits and confirm that they render as expected.


Propose Documentation Changes
-----------------------------

All proposals for documentation edits, including submissions by
project members, require a review process. We use GitHub pull requests
for this purpose. Consult `GitHub
Help <https://help.github.com/articles/about-pull-requests/>`__ for more
information on using pull requests to submit your changes for review.

The Font Bakery source code test suite is executed by 
the Travis CI testing service when you submit a pull request to the
repository. Please verify that all tests pass with your pull request.
Pull requests cannot be merged if any test fails as a result
of your project documentation edits.

The Travis CI build logs can be viewed at
https://travis-ci.org/googlefonts/fontbakery.


Community Guidelines
--------------------

This project follows `Google's Open Source Community Guidelines <https://opensource.google.com/conduct/>`_ and 
the Font Bakery `Code of Conduct <https://github.com/googlefonts/fontbakery/blob/main/CODE_OF_CONDUCT.md>`_.


License
-------

The Font Bakery documentation is licensed under the `CC BY-SA 4.0 International License <https://creativecommons.org/licenses/by-sa/4.0/>`__.
