Data Fitting with SciPy
=======================

**This project is in development and in no way stable.**

Documentation
-------------

Documentation generated from source with
`pdoc <https://pypi.python.org/pypi/pdoc/>`__ for the latest version is
hosted at
`packages.python.org/scipy-data\_fitting/ <http://packages.python.org/scipy-data_fitting/>`__.

To get started quickly, check out the
`examples <https://github.com/razor-x/scipy-data_fitting/tree/master/examples>`__.

Then, refer to the source documentation for details on how to use each
class.

Basic usage
-----------

.. code:: python

    from scipy_data_fitting import Data, Model, Fit, Plot

    # Load data from a CSV file.
    data = Data('linear')
    data.path = 'linear.csv'

    # Create a linear model.
    model = Model('linear')
    model.add_symbols('t', 'v', 'x_0')
    t, v, x_0 = model.get_symbols('t', 'v', 'x_0')
    model.expressions['line'] = v * t + x_0

    # Create the fit using the data and model.
    fit = Fit('linear', data=data, model=model)
    fit.expression = 'line'
    fit.independent = {'symbol': 't', 'name': 'Time', 'units': 's'}
    fit.dependent = {'name': 'Distance', 'units': 'm'}
    fit.parameters = [
        {'symbol': 'x_0', 'value': 1, 'units': 'm'},
        {'symbol': 'v', 'guess': 1, 'units': 'm/s'},
    ]

    # Save the fit result to a json file.
    fit.to_json(fit.name + '.json')

    # Save a plot of the fit to an image file.
    plot = Plot(fit)
    plot.save(fit.name + '.svg')
    plot.close()

Installation
------------

This package is registered on the Python Package Index (PyPI) at
`pypi.python.org/pypi/scipy-data\_fitting <https://pypi.python.org/pypi/scipy-data_fitting>`__.

Add this line to your application's ``requirements.txt``:

::

    scipy-data_fitting

And then execute:

.. code:: bash

    $ pip install -r requirements.txt

Or install it yourself as:

.. code:: bash

    $ pip install scipy-data_fitting

Instead of the package name ``scipy-data_fitting``, you can use this
repository directly with

::

    git+https://github.com/razor-x/scipy-data_fitting.git@master#egg=scipy-data_fitting

Development
-----------

Source Repository
~~~~~~~~~~~~~~~~~

The `source <https://github.com/razor-x/scipy-data_fitting>`__ is hosted
at GitHub. Fork it on GitHub, or clone the project with

.. code:: bash

    $ git clone https://github.com/razor-x/scipy-data_fitting.git

Documentation
~~~~~~~~~~~~~

Generate documentation with pdoc by running

.. code:: bash

    $ make docs

Tests
~~~~~

Run the tests with

.. code:: bash

    $ make tests

Examples
~~~~~~~~

Run an example with

.. code:: bash

    $ python examples/example_fit.py

or run all the examples with

.. code:: bash

    $ make examples

License
-------

This code is licensed under the MIT license.

Warranty
--------

This software is provided "as is" and without any express or implied
warranties, including, without limitation, the implied warranties of
merchantibility and fitness for a particular purpose.
