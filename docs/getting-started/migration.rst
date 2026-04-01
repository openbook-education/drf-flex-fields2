Migration from drf-flex-fields
==============================

If you are currently using the original ``drf-flex-fields`` package, migrating to
``drf-flex-fields2`` is straightforward and requires minimal changes to your codebase.

Prerequisites
^^^^^^^^^^^^^

Before migrating, ensure your project meets the following requirements:

- **Django 6.0** or newer
- **Django REST Framework 3.17.0** or newer

If your project is still on older versions of Django or DRF, you will need to
upgrade them first. The original ``drf-flex-fields`` package should continue to
work with older Django and DRF versions, but ``drf-flex-fields2`` requires the
modern versions listed above.

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
your codebase. This is the only code change required.

**Before:**

.. code-block:: python

   from rest_flex_fields import FlexFieldsModelSerializer


**After:**

.. code-block:: python

   from rest_flex_fields2 import FlexFieldsModelSerializer

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
- Run ``grep -rP "rest_flex_fields(?!2)" .`` to find any remaining old imports
- Check virtualenv/venv activation: ``pip list | grep drf-flex-fields``

**Version conflicts?**

- Verify Django is 6.0+: ``python -m django --version``
- Verify DRF is 3.17.0+: ``python -c "import rest_framework; print(rest_framework.__version__)"``
- Update if needed: ``pip install --upgrade django djangorestframework``

**Other issues?**

- Check the `issue tracker <https://github.com/openbook-education/drf-flex-fields2/issues>`_
- The project is actively maintained and we're happy to help!
