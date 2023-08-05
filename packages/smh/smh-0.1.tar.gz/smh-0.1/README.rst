=======
Spectroscopy Made Hard
=======

:Info: See the `GitHub repository <http://github.com/andycasey/smh/tree/master>`_ for the latest source
:Author: `Andy Casey <acasey@mso.anu.edu.au>`_ (acasey@mso.anu.edu.au)
:License: Don't distribute. This code is only given out to good friends.


This code can be used to measure the stellar parameters and detailed
chemical abundances of a star from high-resolution spectroscopic data,
using a traditional curve-of-growth analysis, and incorporating `MOOG
<http://www.as.utexas.edu/~chris/moog.html>`_.

Requirements
------------

- You will require the `Enthought Python Distribution
  <http://www.enthought.com/products/edudownload.php>`_ (use the
  32-bit version only). This code is free for academic use, but you may
  need to `register using your institution email address
  <https://www2.enthought.com/accounts/register/?next=/licenses/academic>`_.

- The non-interactive version of `MOOG
  <http://www.as.utexas.edu/~chris/moog.html>`_, known as ``MOOGSILENT``. As
  long as you have the appropriate command line tools, you can install
  ``MOOG`` and ``MOOGSILENT`` using ``pip``:

    ``sudo pip install moog``

  (If you don't have ``pip`` installed, you can install it with
  ``easy_install pip`` and then use ``easy_install`` any time you would
  have used ``pip``, `see here why
  <http://stackoverflow.com/questions/3220404/why-use-pip-over-easy-install>`_.)



Installation
------------

The best way to download the code is to use ``git``. If you don't have
``git``, you can `download it for free <http://git-scm.com/downloads>`_. 
Make sure you follow the setup instructions `here <https://help.github.com/articles/set-up-git>`_ 
to make things easier for yourself in the future. If you are asked for a 
password when trying to use the ``sudo`` command, then you should enter 
your administrator password for your machine, not your GitHub
account password. Once ``git`` is set up, use the following command in a 
terminal:

    ``git clone git@github.com:andycasey/smh.git smh``

That will clone the entire repository into a fresh folder called ``smh``.
Whenever there is a new version of the code or a bug-fix, you can download
the latest copy by ``cd``'ing to your ``smh`` directory then using:

    ``git pull``

And that's it! If you encounter unexpected bugs, please copy the entire
stack trace (error log) you get into a new `GitHub issue
<https://github.com/andycasey/smh/issues/new>`_ along with
a detailed description of what you were trying to do when the error
occurred.


Usage
-----

Unless you've set up an alias, just ``cd`` to your ``smh`` directory then use:

    ``python main.py``


Wiki
----

There is an `incomplete Wiki <https://github.com/andycasey/smh/wiki>`_ (that you can contribute to) which takes you
through all the analysis steps in SMH.
