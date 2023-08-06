--------------------------------
django search forms
--------------------------------

The library facilitates creation of search forms in django. It offers a
subclass of forms, that can be inferred authomatically and that will return
a Q object on ``clean()``.

The different fields that are provided in this package represent different
searching logics (search by range, search exact match etc.)
