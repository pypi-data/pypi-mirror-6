*******************
Light Curve Fitting
*******************

*Reference documentation is in* `sncosmo.fit_lc`.

First, have your photometric data in an astropy
`~astropy.table.table.Table`, with a row for each observation. For what this
can look like, see :doc:`photdata`. For now, get an example of
photometric data::

    >>> data = sncosmo.load_example_data()
    >>> print data
         time      band        flux          fluxerr      zp  zpsys
    ------------- ----- ----------------- -------------- ---- -----
          55070.0 sdssg    0.813499900062 0.651728140824 25.0    ab
    55072.0512821 sdssr  -0.0852238865812 0.651728140824 25.0    ab
    55074.1025641 sdssi -0.00681659003089 0.651728140824 25.0    ab
    55076.1538462 sdssz     2.23929135407 0.651728140824 25.0    ab
    55078.2051282 sdssg  -0.0308977349373 0.651728140824 25.0    ab
    55080.2564103 sdssr     2.35450321853 0.651728140824 25.0    ab
    ...

In this data, both the ``band`` column and the ``zpsys`` column
contain strings. These specific bands (e.g., ``'sdssg'``) and
zeropoint system (``'ab'``) are built-ins known to sncosmo, so we can
feed these to any sncosmo function and it will find the right
corresponding `~sncosmo.Bandpass` or `~sncosmo.MagSystem`. The data
could also contain the `~sncosmo.Bandpass` and `~sncosmo.MagSystem`
objects themselves. Or, if it had strings that were not built-ins, you
could register the corresponding `~sncosmo.Bandpass` or
`~sncosmo.MagSystem` using the :doc:`registry`.

Anyway, let's go ahead and fit a SALT2 model to the data::

    >>> model = sncosmo.Model(source='salt2')
    >>> res, fitted_model = sncosmo.fit_lc(data, model,
    ...                                    ['z', 't0', 'x0', 'x1', 'c'],
    ...                                    bounds={'z':(0.3, 0.7)})

Here, we are fitting the parameters of ``model`` to ``data``, and
we've supplied the names of the parameters that we want vary in the fit:
``['z', 't0', 'x0', 'x1', 'c']``. Since we're fitting redshift, we
need to provide bounds on the allowable redshift range. This is the
only parameter that *requires* bounds. Bounds are optional for the
other parameters.

The first object returned, ``res``, is a dictionary that has attribute
access (so ``res['params']`` and ``res.params`` both access the same thing).
You can see what attributes it has::

    >>> res.keys()
    ['errors', 'parameters', 'success', 'cov_names', 'covariance', 'ndof', 'chisq', 'param_names', 'message', 'ncall']

And then access those attributes::

    >>> res.ncall  # number of chi^2 function calls made
    132
    >>> res.ndof  # number of degrees of freedom in fit
    35
    >>> res.chisq  # chi^2 value at minimum
    33.50859337338642

The second object returned is a shallow copy of the input model with
the parameters set to the best fit values. The input model is
unchanged.

    >>> sncosmo.plot_lc(data, model=fitted_model, errors=res.errors)

.. image:: _static/example_lc.png


Fixing parameters (e.g., redshift) and setting initial guesses
==============================================================

Suppose we already know the redshift of the supernova we're trying to
fit.  We want to set the model's redshift to the known value, and then
make sure not to vary `z` in the fit::

    >>> model.set(z=0.5)  # set the model's redshift.
    >>> res, fitted_model = sncosmo.fit_lc(data, model,
    ...                                    ['t0', 'x0', 'x1', 'c'])
