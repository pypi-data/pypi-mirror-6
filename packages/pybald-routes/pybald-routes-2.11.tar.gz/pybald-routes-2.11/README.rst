This is a fork of Ben Bangert's Routes project that includes some custom behaviors that are used by the pybald project. The main difference is that submappers don't automatically concatenate all keyword arguments together in submappers and only the 'prefix' style arguments are generative. All other arguments are allowed to be overridden in submappers (controlelrs, actions, etc...).

Routes is a Python re-implementation of the Rails routes system for mapping
URL's to Controllers/Actions and generating URL's. Routes makes it easy to
create pretty and concise URL's that are RESTful with little effort.

Speedy and dynamic URL generation means you get a URL with minimal cruft
(no big dangling query args). Shortcut features like Named Routes cut down
on repetitive typing.

See `the documentation for installation and usage of Routes <http://readthedocs.org/docs/routes/en/latest/>`_.

