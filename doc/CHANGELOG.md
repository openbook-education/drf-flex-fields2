drf-flex-fields2 Changelog
==========================

2.0.0 (April 2026)
------------------

- Project forked from rsinger86/drf-flex-fields.
- Python package renamed to `drf-flex-fields2`
- Migrated tooling from setuptools to poetry.
- Added CI tooling for automated version upgrades and SBOM generation.
- Migrated source code from Python 2 to Python 3 syntax.
- Fixed usage of deprecated Django APIs.
- Tried to fix many PyLance type errors.


1.0.2 (March 2023)
------------------

- Adds control over whether recursive expansions are allowed and allows setting the max expansion depth. Thanks @andruten!


1.0.1 (March 2023)
------------------

- Various bug fixes. Thanks @michaelschem, @andruten, and @erielias!


1.0.0 (August 2022)
-------------------

- Improvements to the filter backends for generic foreign key handling and docs generation. Thanks @KrYpTeD974 and @michaelschem!


0.9.9 (July 2022)
-----------------

- Fixes bug in `FlexFieldsFilterBackend`. Thanks @michaelschem!
- Adds `FlexFieldsDocsFilterBackend` for schema population. Thanks @Rjevski!


0.9.8 (April 2022)
------------------

- Set expandable fields as the default example for expand query parameters in `coreapi.Field`. Thanks @JasperSui!


0.9.7 (January 2022)
--------------------

- Includes m2m in prefetch_related clause even if they're not expanded. Thanks @pablolmedorado and @ADR-007!


0.9.6 (November 2021)
---------------------

- Make it possible to use wildcard values with sparse fields requests.


0.9.5 (October 2021)
---------------------

- Adds OpenAPI support. Thanks @soroush-tabesh!
- Updates tests for Django 3.2 and fixes deprecation warning. Thanks @giovannicimolin!


0.9.3 (August 2021)
-------------------

- Fixes bug where custom parameter names were not passed when constructing nested serializers. Thanks @Kandeel4411!


0.9.2 (June 2021)
-----------------

- Ensures `context` dict is passed down to expanded serializers. Thanks @nikeshyad!


0.9.1 (June 2021)
-----------------

- No longer auto removes `source` argument if it's equal to the field name.


0.9.0 (April 2021)
------------------

- Allows fully qualified import strings for lazy serializer classes.


0.8.9 (February 2021)
---------------------

- Adds OpenAPI support to experimental filter backend. Thanks @LukasBerka!


0.8.8 (September 2020)
----------------------

- Django 3.1.1 fix. Thansks @NiyazNz!
- Docs typo fix. Thanks @zakjholt!


0.8.6 (September 2020)
----------------------

- Adds `is_included` utility function.


0.8.5 (May 2020)
----------------

- Adds options to customize parameter names and wildcard values. Closes #10.


0.8.1 (May 2020)
----------------

- Fixes #44, related to the experimental filter backend. Thanks @jsatt!


0.8.0 (April 2020)
------------------

- Adds support for `expand`, `omit` and `fields` query parameters for non-GET requests.
  - The common use case is creating/updating a model instance and returning a serialized response with expanded fields
  - Thanks @kotepillar for raising the issue (#25) and @Crocmagnon for the idea of delaying field modification to `to_representation()`.


0.7.5 (February 2020)
---------------------

- Simplifies declaration of `expandable_fields`
  - If using a tuple, the second element - to define the serializer settings - is now optional.
  - Instead of a tuple, you can now just use the serializer class or a string to lazily reference that class.
  - Updates documentation.


0.7.0 (February 2020)
---------------------

- Adds support for different ways of passing arrays in query strings. Thanks @sentyaev!
- Fixes attribute error when map is supplied to split levels utility function. Thanks @hemache!


0.6.1 (September 2019)
----------------------

- Adds experimental support for automatically SQL query optimization via a `FlexFieldsFilterBackend`. Thanks ADR-007!
- Adds CircleCI config file. Thanks mikeIFTS!
- Moves declaration of `expandable_fields` to `Meta` class on serialzer for consistency with DRF (will continue to support declaration as class property)
- Python 2 is no longer supported. If you need Python 2 support, you can continue to use older versions of this package.


0.5.0 (April 2019)
------------------

- Added support for `omit` keyword for field exclusion. Code clean up and improved test coverage.


0.3.4 (May 2018)
----------------

- Handle case where `request` is `None` when accessing request object from serializer. Thanks @jsatt!


0.3.3 (April 2018)
------------------

- Exposes `FlexFieldsSerializerMixin` in addition to `FlexFieldsModelSerializer`. Thanks @jsatt!