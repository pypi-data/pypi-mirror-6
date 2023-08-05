A sphinx theme plugin extension.

.. warning::

   For users:
   sphinxjp.themecore will be deprecated. Please use theme plugins with
   Sphinx-1.2.


.. warning::

   For theme developers:
   sphinxjp.themecore's 'sphinx_themes' entry point feature is provided on the
   Sphinx from 1.2(b3) release. However 'sphinx_directives' feature is not
   provided by the Sphinx.

   If your theme plugin provides only 'sphinx_themes' entry point, you need
   remove ``extensions = ['sphinxjp.themecore']`` line from your documentation
   and remove ``sphinxjp.themecore`` dependency from install_requires in the
   setup.py. There is a example of change to support both before and after
   Sphinx-1.2:
   https://bitbucket.org/shimizukawa/sphinxjp.themes.sphinxjp/commits/c66313e

   If your theme plugin provides 'sphinx_directives' entry point too,
   additionaly you need write your setup() function in your extension root
   package instead of such as setup_directive() and need change your
   documentation's installation section with like:
   "set ``extensions=["sphinxjp.themes.s6"]`` instead of 'sphinx.themecore'".
   There is a example of change to support both before and after Sphinx-1.2:
   https://bitbucket.org/shimizukawa/sphinxjp.themes.s6/commits/ed91ae537


Features
========
* provide theme template collection by using setuptools plugin mechanism.


Setup
=====
Make environment with easy_install::

    $ easy_install sphinxjp.themecore


Make your plugins
===================
themes
-------
If you want to integrate new theme, write ``sphinx_themes`` entry_points
in your setup.py::

    entry_points = """
        [sphinx_themes]
        path = sphinxjp.themes.s6:get_path
    """

and write `get_path` function that return path of ``Sphinx themes``.
``Sphinx themes`` directory include one or more theme directories.

directives
-----------
If you want to integrate new directive, write ``sphinx_directives``
entry_points in your setup.py::

    entry_points = """
        [sphinx_directives]
        setup = sphinxjp.themes.s6:setup_directives
    """

and write `setup_directives` function that receive `app` argument
and return None. setup_directives is same as sphinx extension's setup
function. See Sphinx extension document for more information.


Requirements
============
* Python 2.4 or later (not support 3.x)
* sphinx 1.0.x


License
=======
Licensed under the `MIT license <http://www.opensource.org/licenses/mit-license.php>`_ .
See the LICENSE file for specific terms.

