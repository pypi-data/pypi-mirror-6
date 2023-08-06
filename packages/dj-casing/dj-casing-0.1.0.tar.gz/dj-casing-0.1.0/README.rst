===================================
dj-casing for casE iNsensitive UrLS
===================================

Allow case insensitive URLs while enforcing the right URL.

Apply the `case_insenstive` decorator if you have URLs which should match
regardless of case, but you don't want those URLs hanging out there when a user
visits.

Installation
------------

Install dj-casing::

    pip install djcasing

Decorating a view
-----------------

Then use it in a project::

    from djcasing import case_insenstive


    @case_insensitive
    def some_view(request, urlarg_one, urlarg_two):
        # do stuff here

Now URLs of the form `http://example.com/BobsWorld/PageOne/` can be matched to
`http://examle.com/bobsworld/pageone` and visitors will be immediately
redirected to the latter URL.

License
-------

BSD licensed.
