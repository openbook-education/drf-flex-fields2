Migration from drf-flex-fields
==============================

If you are currently using the original ``drf-flex-fields`` package, migrating to
``drf-flex-fields2`` is straightforward and requires minimal changes to your codebase.

Installation
^^^^^^^^^^^^

Assuming you are using ``pip`` for dependency management. Adapt to your package
manager, as needed:

1. **Uninstall the old package:**

   .. code-block:: bash

      pip uninstall drf-flex-fields

2. **Install drf-flex-fields2:**

   .. code-block:: bash

      pip install drf-flex-fields2

Update Imports
^^^^^^^^^^^^^^

Replace all imports of ``rest_flex_fields`` with ``rest_flex_fields2`` throughout
your codebase.

If you imported symbols from the package root, update those to
module-level imports instead. Package-level re-exports were removed to
fix import cycles during Django initialization.

**Before:**

.. code-block:: python

    from rest_flex_fields import FlexFieldsModelSerializer


**After (module-level import):**

.. code-block:: python

    from rest_flex_fields2.serializers import FlexFieldsModelSerializer

Update Django Settings
^^^^^^^^^^^^^^^^^^^^^^

In your Django ``settings.py`` rename the variable ``REST_FLEX_FIELDS``
to ``REST_FLEX_FIELDS2``.

API Compatibility
^^^^^^^^^^^^^^^^^

The ``drf-flex-fields2`` API is fully compatible with the original ``drf-flex-fields``
package. All serializers, mixins, filters, and configuration options work exactly
the same way.

**Stability:** No breaking changes are planned in the foreseeable future.

**Future guarantee:** If breaking changes ever become necessary, the
``drf-flex-fields2`` project will strictly follow `semantic versioning
<https://semver.org/>`_. This means you can safely update to patch and minor
versions (e.g., from 2.0.0 to 2.1.5) without worrying about breaking changes.
Breaking changes will only occur in major version releases (e.g., 2.x to 3.0),
and will be clearly documented in the changelog.

Testing Your Migration
^^^^^^^^^^^^^^^^^^^^^^

After updating the imports, run your test suite to ensure everything works correctly:

.. code-block:: bash

    python manage.py test

If you don't have tests yet, we recommend adding them to your project to catch
any integration issues early.

Troubleshooting
^^^^^^^^^^^^^^^

**Import errors after migration?**

- Ensure you've updated all imports from ``rest_flex_fields`` to ``rest_flex_fields2``
- Replace package-level imports with module-level imports (for example,
  ``from rest_flex_fields2.serializers import FlexFieldsModelSerializer``)
- Run ``grep -rP "rest_flex_fields(?!2)" .`` to find any remaining old imports
- Check virtualenv/venv activation: ``pip list | grep drf-flex-fields``

**Other issues?**

- Check the `issue tracker <https://github.com/openbook-education/drf-flex-fields2/issues>`_
- The project is actively maintained and we're happy to help!
