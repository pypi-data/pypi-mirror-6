Schema validation for Python data structures
============================================

Basic validation for Python data structures in a mostly declarative
form (there is an escape hatch in "extraValidation" callables).

Validation errors are reported as both a path within the data
structure (sequence of indices or keys) and a descriptive message
(string).

Typical usage::

    data = json.load(some_file) # or pickle, or ...
    errors = dataschema.Validator(my_schema).validate(data)
    if errors:
        for path, message in errors:
            # Report error `message` at path `path`.
    else:
        # Any data access or application-specific validation can now
        # rely on properties of my_schema (e.g. minimum number of
        # elements in a sequence, data types of elements, presence of
        # certain keys in a dict, etc.).

See the unit tests for schema examples.

There are a few limitations (only string keys for any dictionaries in
data) and a more fully Pythonic validator might focus on interfaces
and abstract base classes over concrete types.  However, dataschema is
a great improvement over ad hoc validation code for many uses today.
