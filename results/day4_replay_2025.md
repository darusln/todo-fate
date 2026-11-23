# Day 4: replayed deployment

As if the tool had been run on 1 November of 2025. At each
date the model was trained only on cohorts before that year (labels already known on
that date), then ranked the TODOs each project had added in the year before.
Outcomes are what really happened one year later, using the dataset's labelling rule.

## Pooled over all replayed repos (794 TODOs, 26% resolved)

| | ROC-AUC | PR-AUC | Precision | Recall | F1 | Rot precision@20 |
|---|---|---|---|---|---|---|
| Always predict rotting | 0.500 | 0.275 | 0.000 | 0.000 | 0.000 | 80% |
| Rule: deadline OR removal | 0.597 | 0.366 | 0.415 | 0.386 | 0.400 | 90% |
| **Logistic regression** | 0.597 | 0.438 | 0.388 | 0.285 | 0.329 | 70% |

## Per repo

| Repo | Young TODOs | Resolved within a year | ROC-AUC | PR-AUC | F1 | Rot precision@k |
|---|---|---|---|---|---|---|
| pytest-dev/pytest | 18 | 4 (22%) | 0.357 | 0.208 | 0.000 | 78% (k=18) |
| sympy/sympy | 58 | 4 (7%) | 0.509 | 0.091 | 0.000 | 95% (k=20) |
| sqlalchemy/sqlalchemy | 18 | 0 (0%) | n/a | n/a | 0.000 | 100% (k=18) |
| django/django | 8 | 0 (0%) | n/a | n/a | 0.000 | 100% (k=8) |
| pypa/pip | 4 | 1 (25%) | 1.000 | 1.000 | 0.667 | 75% (k=4) |
| pypa/setuptools | 21 | 6 (29%) | 0.778 | 0.644 | 0.364 | 75% (k=20) |
| ipython/ipython | 12 | 0 (0%) | n/a | n/a | 0.000 | 100% (k=12) |
| pandas-dev/pandas | 33 | 7 (21%) | 0.549 | 0.308 | 0.333 | 85% (k=20) |
| numpy/numpy | 4 | 1 (25%) | 1.000 | 1.000 | 0.000 | 75% (k=4) |
| scipy/scipy | 61 | 15 (25%) | 0.499 | 0.263 | 0.000 | 70% (k=20) |
| scikit-learn/scikit-learn | 159 | 59 (37%) | 0.814 | 0.779 | 0.608 | 85% (k=20) |
| networkx/networkx | 1 | 0 (0%) | n/a | n/a | 0.000 | 100% (k=1) |
| astropy/astropy | 24 | 1 (4%) | 0.957 | 0.500 | 0.000 | 100% (k=20) |
| dask/dask | 58 | 0 (0%) | n/a | n/a | 0.000 | 100% (k=20) |
| apache/airflow | 235 | 91 (39%) | 0.439 | 0.343 | 0.104 | 65% (k=20) |
| ansible/ansible | 58 | 11 (19%) | 0.536 | 0.244 | 0.000 | 75% (k=20) |
| saltstack/salt | 22 | 7 (32%) | 0.733 | 0.521 | 0.000 | 65% (k=20) |

Rot precision@k: of the k TODOs the model flagged as most at risk, the share
still there a year later. Compare with each repo's own rotting rate.

## The rankings, for qualitative review

### pytest-dev/pytest

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.79 | [move common code into superclass](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/raises.py#L696) | still there |
| 2025 | 0.79 | [it instructs to use `-v` to print leading text, but that doesn't work](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/raises.py#L513) | **resolved** |
| 2025 | 0.77 | [harmonize with ExceptionInfo.match](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/raises.py#L495) | still there |
| 2025 | 0.74 | [Try to use FixtureFunctionDefinition instead of the marker](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/fixtures.py#L150) | still there |
| 2025 | 0.74 | [this line is not great, should maybe follow the same format as the other and say](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/python/raises_group.py#L697) | still there |
| 2025 | 0.71 | [paramspec/return type annotation tracking and storing](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/fixtures.py#L1256) | still there |
| 2025 | 0.69 | [did not match Exceptiongroup('h(ell)o', ...) ?](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/python/raises_group.py#L635) | still there |
| 2025 | 0.67 | [bad sentence structure](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/python/raises_group.py#L49) | **resolved** |
| 2025 | 0.60 | [leaving this one formatted differently for now to not change](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/python/raises_group.py#L1100) | **resolved** |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.41 | [Remove the hacky split once the collection structure](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/src/_pytest/main.py#L993) | still there |
| 2025 | 0.43 | [these are different for some reason(?)](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/typing_raises_group.py#L18) | still there |
| 2025 | 0.46 | [should be a test failure or error](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_unraisableexception.py#L384) | still there |
| 2025 | 0.48 | [Should be a test failure or error. Currently the exception](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_unraisableexception.py#L318) | still there |
| 2025 | 0.48 | [Should be a test failure or error. Currently the exception](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_unraisableexception.py#L285) | still there |
| 2025 | 0.49 | [should be a test failure or error](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_threadexception.py#L244) | still there |
| 2025 | 0.49 | [should be a test failure or error](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_threadexception.py#L216) | still there |
| 2025 | 0.58 | [do we want repr(type) or type.__name__ ?](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/python/raises_group.py#L1111) | **resolved** |
| 2025 | 0.59 | [should be warnings=1, but the outcome has already come out](https://github.com/pytest-dev/pytest/blob/5eaad82074c08b63ee6667d9760d795ea16e73f9/testing/test_unraisableexception.py#L356) | still there |
### sympy/sympy

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.93 | [The line below uses == rather than = which means](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/combinatorics/coset_table.py#L817) | still there |
| 2025 | 0.92 | [not simplify should be not simplify_flag. mypy correctly complains](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/solvers/ode/single.py#L1728) | **resolved** |
| 2025 | 0.92 | [Using expand(complex=True) might look nice in simple cases but is a](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyroots.py#L444) | still there |
| 2025 | 0.92 | [Pass in domain parameter](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/galoistools.py#L2333) | still there |
| 2025 | 0.91 | [Only RepMatrix has _rep ...](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/matrices/eigen.py#L293) | still there |
| 2025 | 0.91 | [Better name?](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/integrals/risch.py#L799) | still there |
| 2025 | 0.90 | [abs not defined for all domains](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/compatibility.py#L493) | still there |
| 2025 | 0.90 | [abs not defined for all domains](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/compatibility.py#L497) | still there |
| 2025 | 0.89 | [.atoms(Atom) is not the same as .atoms()](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/matrices/matrixbase.py#L1588) | still there |
| 2025 | 0.88 | [roots_quadratic should be improved to handle signs under the radical](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/tests/test_polyroots.py#L327) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.69 | [Maybe remove the dunder methods like __add__? It is not clear that](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyclasses.py#L1234) | still there |
| 2025 | 0.70 | [Remove the ignore flag](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/core/symbol.py#L452) | still there |
| 2025 | 0.71 | [This should only be for some domains (can fail over ZZ)](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyclasses.py#L1620) | still there |
| 2025 | 0.71 | [if other methods for computing pade approximants are implemented,](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/series/approximants.py#L403) | still there |
| 2025 | 0.71 | [Remove this. It should be defined somewhere else and not part](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/orderings.py#L275) | still there |
| 2025 | 0.72 | [Does this fail for GF(p)[x]?](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyclasses.py#L2364) | still there |
| 2025 | 0.72 | [Does this fail for GF(p)[x]?](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyclasses.py#L2357) | still there |
| 2025 | 0.72 | [Does this fail for GF(p)[x]?](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/polyclasses.py#L2330) | still there |
| 2025 | 0.78 | [This function doesn't seem to be used anywhere. Delete it.](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/matrices/dense.py#L108) | still there |
| 2025 | 0.78 | [mypy does not understand this for some reason (likely a bug)](https://github.com/sympy/sympy/blob/c1097516c793b0364c4f3fe2eeb66b15a94eedfd/sympy/polys/densebasic.py#L79) | still there |
### sqlalchemy/sqlalchemy

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.85 | [test this case](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/lib/sqlalchemy/engine/cursor.py#L1720) | still there |
| 2025 | 0.84 | [SET is a string as far as configuration but does not act like](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/lib/sqlalchemy/dialects/mysql/enumerated.py#L113) | still there |
| 2025 | 0.79 | [this code is uncovered and in all likelihood is not included](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/lib/sqlalchemy/sql/elements.py#L761) | still there |
| 2025 | 0.79 | [mypy requires the _TypedSelectable overloads in all compound select](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/lib/sqlalchemy/sql/_selectable_constructors.py#L107) | still there |
| 2025 | 0.79 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms_future_anno_sync.py#L171) | still there |
| 2025 | 0.79 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms_future_anno_sync.py#L321) | still there |
| 2025 | 0.79 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms_future_anno_sync.py#L1338) | still there |
| 2025 | 0.79 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms_future_anno_sync.py#L1363) | still there |
| 2025 | 0.77 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms.py#L162) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.64 | [the following do not error because _SelectStatementForCompoundArgument](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/typing/plain_files/sql/common_sql_element.py#L213) | still there |
| 2025 | 0.66 | [in the](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/typing/plain_files/sql/common_sql_element.py#L216) | still there |
| 2025 | 0.66 | [these are false negatives](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/base/test_typing_utils.py#L559) | still there |
| 2025 | 0.75 | [add an assertion?](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_tm_future_annotations_sync.py#L758) | still there |
| 2025 | 0.75 | [add an assertion?](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_typed_mapping.py#L749) | still there |
| 2025 | 0.76 | [this seems like a bug. maybe just document it?](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/sql/test_insert_exec.py#L3065) | still there |
| 2025 | 0.77 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms.py#L1348) | still there |
| 2025 | 0.77 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms.py#L1325) | still there |
| 2025 | 0.77 | [get this test to work with future anno mode as well](https://github.com/sqlalchemy/sqlalchemy/blob/2bd8e962c7b8e0abf7396ac3a8ad82a9334a62e1/test/orm/declarative/test_dc_transforms.py#L310) | still there |
### django/django

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.86 | [The deletion UX can be confusing when dealing with cascading](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/contrib/admin/widgets.py#L295) | still there |
| 2025 | 0.84 | [It might be possible to trim more joins from the start of](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/db/models/sql/query.py#L2695) | still there |
| 2025 | 0.83 | [LANG_OVERRIDES.get(lang, lang)](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/scripts/manage_translations.py#L131) | still there |
| 2025 | 0.81 | [Adapt timezone information. See:](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/contrib/gis/gdal/field.py#L189) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.49 | [Drop ImportError and KeyError when dropping support for PY312.](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/tests/auth_tests/test_management.py#L136) | still there |
| 2025 | 0.55 | [Drop ImportError and KeyError when dropping support for PY312.](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/contrib/auth/management/__init__.py#L199) | still there |
| 2025 | 0.75 | [this currently assumes that upload handlers store the file as](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/http/multipartparser.py#L409) | still there |
| 2025 | 0.81 | [Research way to find a more specific geometry field type](https://github.com/django/django/blob/05ba1a9228128614fb3c475f1c4bdf0160f44dba/django/contrib/gis/db/backends/oracle/introspection.py#L35) | still there |
### pypa/pip

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.93 | [if the distribution is a zipped egg, location has a trailing /](https://github.com/pypa/pip/blob/7daeda1cb53546615a8c75161028b8121321119e/src/pip/_internal/metadata/base.py#L229) | still there |
| 2025 | 0.91 | [We use normalized_dist_location because dist_location my contain](https://github.com/pypa/pip/blob/7daeda1cb53546615a8c75161028b8121321119e/src/pip/_internal/req/req_uninstall.py#L511) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.30 | [replace this with slots=True when dropping Python 3.9 support.](https://github.com/pypa/pip/blob/7daeda1cb53546615a8c75161028b8121321119e/src/pip/_internal/req/req_file.py#L103) | **resolved** |
| 2025 | 0.44 | [we want to skip building and installing pip when nox's --no-install](https://github.com/pypa/pip/blob/7daeda1cb53546615a8c75161028b8121321119e/noxfile.py#L84) | still there |
### pypa/setuptools

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.86 | [Is marking as static contents coming from modules too optimistic?](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/expand.py#L186) | still there |
| 2025 | 0.85 | [Is marking as static contents coming from files too optimistic?](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/setupcfg.py#L400) | still there |
| 2025 | 0.83 | [`license-file` is currently not considered in the context of `dynamic`.](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_apply_pyprojecttoml.py#L468) | still there |
| 2025 | 0.83 | [`license-file` is currently not considered in the context of `dynamic`.](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_apply_pyprojecttoml.py#L488) | still there |
| 2025 | 0.82 | [Is it completely safe to assume static?](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_apply_pyprojecttoml.py#L191) | still there |
| 2025 | 0.82 | [Is it completely safe to assume static?](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_apply_pyprojecttoml.py#L220) | still there |
| 2025 | 0.79 | [License-File is complicated because the user gives globs that are expanded](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/_core_metadata.py#L316) | still there |
| 2025 | 0.77 | [check for `include-group` cycles (can be conditional to graphlib)](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/extra_validations.py#L78) | still there |
| 2025 | 0.75 | [pyright is still upset even with # pyright: ignore[reportAssignmentType]](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/_normalization.py#L178) | still there |
| 2025 | 0.73 | [Once plugins/customizations had the chance to catch up, replace](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/command/editable_wheel.py#L291) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.01 | [enforce it with format?)'}}}, 'required': ['requires']}, 'project': {'$schema': 'http://js](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/fastjsonschema_validations.py#L154) | **resolved** |
| 2025 | 0.01 | [enforce it with format?)'}}}, 'required': ['requires']}, 'project': {'$schema': 'http://js](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/fastjsonschema_validations.py#L35) | **resolved** |
| 2025 | 0.27 | [Remove after deprecation warning is solved](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/_static.py#L24) | still there |
| 2025 | 0.32 | [After deprecation period raise NotImplementedError instead of warning](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/_static.py#L41) | still there |
| 2025 | 0.44 | [Remove this test after deprecation period is over](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/tests/test_bdist_wheel.py#L668) | still there |
| 2025 | 0.55 | [Do we need this after the deprecation discussed in #4892, #4896??](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/_core_metadata.py#L298) | still there |
| 2025 | 0.59 | [Should we add a due date? It may affect old/unmaintained](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/dist.py#L443) | still there |
| 2025 | 0.62 | [add regex pattern or format?'}}, 'required': ['content-type']}]}]}, 'requires-python': {'t](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/fastjsonschema_validations.py#L1349) | **resolved** |
| 2025 | 0.62 | [add regex pattern or format?'}}, 'required': ['content-type']}]}]}, 'requires-python': {'t](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/fastjsonschema_validations.py#L1044) | **resolved** |
| 2025 | 0.62 | [add regex pattern or format?'}}, 'required': ['content-type']}]}]}, 'requires-python': {'t](https://github.com/pypa/setuptools/blob/d198e86f57231e83de87975c5c82bc40c196da79/setuptools/config/_validate_pyproject/fastjsonschema_validations.py#L988) | **resolved** |
### ipython/ipython

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.78 | [investigate Toke.Line here, likely Line](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/debugger.py#L713) | still there |
| 2025 | 0.77 | [investigate Toke.Line here, likely LineEm,](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/debugger.py#L702) | still there |
| 2025 | 0.77 | [investigate Token.Line here](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/debugger.py#L777) | still there |
| 2025 | 0.73 | [port to magic_arguments as currently this is duplicated in IPCompleter._extract_code](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/magics/execution.py#L320) | still there |
| 2025 | 0.73 | [port to magic_arguments as currently this is duplicated in IPCompleter._extract_code](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/magics/execution.py#L1141) | still there |
| 2025 | 0.72 | [no default ?](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/doctb.py#L101) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.54 | [should this be finnally ?](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/testing/decorators.py#L128) | still there |
| 2025 | 0.60 | [deprecate this](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/terminal/interactiveshell.py#L360) | still there |
| 2025 | 0.66 | [support class decorators?](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/guarded_eval.py#L801) | still there |
| 2025 | 0.66 | [populate transient_locals](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/guarded_eval.py#L918) | still there |
| 2025 | 0.67 | [no default ?](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/ultratb.py#L459) | still there |
| 2025 | 0.67 | [no default](https://github.com/ipython/ipython/blob/72bb67ee8f57cb347ba358cce786c3fa87c470b9/IPython/core/ultratb.py#L1013) | still there |
### pandas-dev/pandas

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.80 | [better place to do this?](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/indexes/base.py#L6698) | still there |
| 2025 | 0.79 | [By using `zero_copy_only` it may be possible to implement this](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/arrays/arrow/array.py#L845) | still there |
| 2025 | 0.79 | [use ser.replace(np.nan, NA) once that works](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/series/methods/test_rank.py#L293) | still there |
| 2025 | 0.79 | [Replace with pc.utf8_zfill when supported by arrow](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/arrays/arrow/array.py#L2826) | **resolved** |
| 2025 | 0.76 | [Test is incorrect when not using_infer_string.](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/io/pytables/test_append.py#L256) | **resolved** |
| 2025 | 0.75 | [these can work but need to update ser construction.](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/series/methods/test_rank.py#L283) | still there |
| 2025 | 0.75 | [also the ArrowDtype analogues?](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/internals/blocks.py#L1519) | still there |
| 2025 | 0.75 | [should this be object with `not using_nan_is_na` to avoid](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/arrays/floating/test_to_numpy.py#L17) | still there |
| 2025 | 0.74 | [flags passed separately by user are ignored](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/arrays/string_arrow.py#L379) | **resolved** |
| 2025 | 0.73 | [also the ArrowDtype analogues?](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/frame.py#L11557) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.10 | [Once the deprecation here is enforced, this method can be](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/arrays/string_.py#L374) | still there |
| 2025 | 0.21 | [warnings.catch_warnings can be removed when numpy>2.3.0](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/dtypes/common.py#L1879) | still there |
| 2025 | 0.31 | [Cannot rely on Numpy returning view after version 2.3](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/copy_view/test_methods.py#L923) | still there |
| 2025 | 0.48 | [make this work for string dtype](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/io/pytables/test_read.py#L185) | **resolved** |
| 2025 | 0.49 | [make this work for string dtype](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/io/pytables/test_round_trip.py#L438) | **resolved** |
| 2025 | 0.52 | [make this work for string dtype](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/io/pytables/test_put.py#L302) | **resolved** |
| 2025 | 0.59 | [could also do this for NDArrayBackedEA cases?](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/generic.py#L9951) | still there |
| 2025 | 0.60 | [this will be unnecessary](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/core/internals/managers.py#L1171) | still there |
| 2025 | 0.64 | [wrong place for this override](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/extension/base/interface.py#L69) | still there |
| 2025 | 0.65 | [we should infer int64 dtype here?](https://github.com/pandas-dev/pandas/blob/82fa27153e5b646ecdb78cfc6ecf3e1750443892/pandas/tests/arrays/string_/test_string.py#L586) | still there |
### numpy/numpy

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.78 | [It seems better to always store a valid fill_value, the oddity](https://github.com/numpy/numpy/blob/779929c42dd5dfa32f07f1311233abea9f026310/numpy/ma/core.py#L483) | still there |
| 2025 | 0.78 | [For methods with a docstring "Parameters" section, that do not already](https://github.com/numpy/numpy/blob/779929c42dd5dfa32f07f1311233abea9f026310/numpy/ma/core.py#L7086) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.54 | [remove/deprecate once `ma.extras._fromnxfunction.getdoc` no longer uses it](https://github.com/numpy/numpy/blob/779929c42dd5dfa32f07f1311233abea9f026310/numpy/ma/core.py#L137) | **resolved** |
| 2025 | 0.58 | [ugly workaround for isinf bug.](https://github.com/numpy/numpy/blob/779929c42dd5dfa32f07f1311233abea9f026310/numpy/_core/tests/test_umath_complex.py#L342) | still there |
### scipy/scipy

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.92 | [if cov.ndim == 2 and limits.ndim == 1, can avoid apply_along_axis](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/stats/_multivariate.py#L653) | still there |
| 2025 | 0.89 | [consider using stats.quantile, which is natively Array API compatible](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/signal/_signaltools.py#L4048) | still there |
| 2025 | 0.89 | [internally, _b_orthonormalize tries to invert an ill-conditioned matrix](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/sparse/linalg/_eigen/lobpcg/tests/test_lobpcg.py#L140) | still there |
| 2025 | 0.88 | [simplify when data-apis/array-api-compat#147 is available](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/signal/_signaltools.py#L4264) | **resolved** |
| 2025 | 0.87 | [solve_banded does not suppport batched `ab` matrices; loop manually](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/interpolate/_bsplines.py#L2438) | **resolved** |
| 2025 | 0.86 | [As of 1.14.1 it isn't possible to build SciPy with ILP64,](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/linalg/_decomp_svd.py#L157) | **resolved** |
| 2025 | 0.86 | [True->1, False->0](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/signal/_filter_design.py#L158) | still there |
| 2025 | 0.84 | [; b upcasts a?](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/linalg/_basic.py#L217) | still there |
| 2025 | 0.84 | [fminbound array API](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/signal/_filter_design.py#L4139) | still there |
| 2025 | 0.82 | [This special case handling is mainly a result of Array API limitations.](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/spatial/transform/_rotation.py#L2213) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.41 | [revert this once the warning bug fix in sksparse is merged/released](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/optimize/_trustregion_constr/projections.py#L61) | still there |
| 2025 | 0.46 | [revert this suppress_warning once the warning bug fix in](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/optimize/_linprog_ip.py#L92) | still there |
| 2025 | 0.54 | [CI failures with GROW7 as of gh-21565](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/benchmarks/benchmarks/optimize_linprog.py#L45) | still there |
| 2025 | 0.54 | [CI failures with GROW7 as of gh-21565](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/benchmarks/benchmarks/optimize_linprog.py#L20) | still there |
| 2025 | 0.54 | [quietly remove float128 and complex256](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/signal/tests/test_filter_design.py#L410) | still there |
| 2025 | 0.59 | [narrow down to _fblas.error](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/linalg/tests/test_blas.py#L822) | **resolved** |
| 2025 | 0.59 | [narrow down to _fblas.error](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/linalg/tests/test_blas.py#L776) | **resolved** |
| 2025 | 0.65 | [this can return other backends e.g. tpu but they're unsupported in scipy](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/_lib/_array_api.py#L1023) | still there |
| 2025 | 0.65 | [this can return other backends e.g. tpu but they're unsupported in scipy](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/_lib/_array_api.py#L1020) | still there |
| 2025 | 0.68 | [non-deterministic rng](https://github.com/scipy/scipy/blob/8ca0da274e0ee619d923dc76fa14dcabcd568730/scipy/linalg/tests/test_decomp.py#L48) | still there |
### scikit-learn/scikit-learn

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.90 | [nan is only supported for dense arrays, but we set this for](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/tree/_classes.py#L1102) | **resolved** |
| 2025 | 0.90 | [nan is only supported for dense arrays, but we set this for](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/tree/_classes.py#L1445) | **resolved** |
| 2025 | 0.88 | [this test is thread-unsafe because it uses _libsvm.cross_validation:](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/svm/tests/test_svm.py#L67) | still there |
| 2025 | 0.87 | [is the return type a list or a tuple](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/externals/array_api_compat/torch/_aliases.py#L833) | **resolved** |
| 2025 | 0.86 | [Account for other backends.](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/externals/array_api_compat/common/_helpers.py#L264) | still there |
| 2025 | 0.85 | [This won't handle dask unknown shapes](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/externals/array_api_compat/dask/array/_aliases.py#L224) | still there |
| 2025 | 0.84 | [Consider whether pa1 and pa2 could also work for other losses.](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/linear_model/_stochastic_gradient.py#L159) | still there |
| 2025 | 0.84 | [probably related to the thread-safety bug tracked at:](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/neighbors/tests/test_neighbors.py#L158) | still there |
| 2025 | 0.84 | [respect device keyword?](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/externals/array_api_compat/dask/array/_aliases.py#L65) | still there |
| 2025 | 0.84 | [respect device keyword?](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/externals/array_api_compat/dask/array/_aliases.py#L96) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.03 | [Remove when minimum pyarrow version is 17.0.0](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/utils/fixes.py#L388) | **resolved** |
| 2025 | 0.05 | [remove copy warning filter](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/tests/test_docstring_parameters.py#L175) | still there |
| 2025 | 0.06 | [Remove in 1.9](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/metrics/_plot/tests/test_roc_curve_display.py#L325) | **resolved** |
| 2025 | 0.08 | [remove when deprecated `base_estimator` is removed](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/tests/test_multioutput.py#L870) | **resolved** |
| 2025 | 0.08 | [remove warning filter](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/manifold/tests/test_mds.py#L205) | **resolved** |
| 2025 | 0.08 | [remove warning filter](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/manifold/tests/test_mds.py#L178) | **resolved** |
| 2025 | 0.08 | [remove warning filter](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/manifold/tests/test_mds.py#L139) | **resolved** |
| 2025 | 0.08 | [remove warning filter](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/manifold/tests/test_mds.py#L125) | **resolved** |
| 2025 | 0.08 | [remove filterwarnings after the deprecation of liblinear multiclass](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/svm/tests/test_bounds.py#L17) | **resolved** |
| 2025 | 0.08 | [Remove when Python min version >= 3.12.](https://github.com/scikit-learn/scikit-learn/blob/ce27c87947098f01eeaba624cc001c9994c9ec4e/sklearn/utils/fixes.py#L334) | **resolved** |
### networkx/networkx

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
### astropy/astropy

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.87 | [for not NUMPY_LT_2_0, try changing this to:](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/misc/ecsv.py#L772) | still there |
| 2025 | 0.86 | [it would be nice to upstream this to scipy and then use it here.](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/cosmology/_src/funcs/optimize.py#L28) | still there |
| 2025 | 0.85 | [better way to check for an iterable of str?](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/misc/ecsv.py#L1178) | still there |
| 2025 | 0.85 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/fits/scripts/fitsheader.py#L407) | still there |
| 2025 | 0.84 | [would be nice if the first two could work, but currently](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/coordinates/tests/test_shape_manipulation.py#L371) | still there |
| 2025 | 0.83 | [for an ndarray output, one could in principle](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/units/quantity_helper/function_helpers.py#L268) | still there |
| 2025 | 0.83 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/fits/scripts/fitsdiff.py#L101) | still there |
| 2025 | 0.82 | [solve both of the above by defining inside get_erfa_helpers?](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/units/quantity_helper/erfa.py#L8) | still there |
| 2025 | 0.80 | [avoid using a private attribute from table.](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/utils/masked/core.py#L1446) | still there |
| 2025 | 0.80 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/visualization/scripts/fits2bitmap.py#L139) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.47 | [Gaussian1DKernel sometimes fails check_pickling_recovery()](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/convolution/tests/test_pickle.py#L14) | still there |
| 2025 | 0.54 | [the following fails if explicit_set is False because wcsset](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/wcs/tests/test_wcs.py#L2218) | **resolved** |
| 2025 | 0.62 | [comment out for now, as it causes TypeError in edge cases with MaskedColumn](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/timeseries/tests/test_downsample.py#L360) | still there |
| 2025 | 0.63 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/wcs/wcslint.py#L17) | still there |
| 2025 | 0.63 | [recarray removes the "numpy.record" mention in the dtype repr,](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/fits/fitsrec.py#L487) | still there |
| 2025 | 0.64 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/votable/volint.py#L15) | still there |
| 2025 | 0.73 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/samp/hub_script.py#L22) | still there |
| 2025 | 0.76 | [use astropy.units.quantity_helpers.function_helpers.FunctionAssigner?](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/utils/shapes.py#L316) | still there |
| 2025 | 0.76 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/io/fits/scripts/fitsinfo.py#L60) | still there |
| 2025 | 0.76 | [pass suggest_on_error as kwarg when PYTHON_LT_14 is dropped](https://github.com/astropy/astropy/blob/746796143cb666c4349caaa4494b1a6bb90f7349/astropy/table/scripts/showtable.py#L114) | still there |
### dask/dask

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.87 | [not sure about this](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/random.py#L986) | still there |
| 2025 | 0.86 | [Decompose p2p Into transfer/barrier + unpack](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_shuffle.py#L614) | still there |
| 2025 | 0.85 | [, handle setting index with other frame](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_shuffle.py#L929) | still there |
| 2025 | 0.85 | [handle non-trivial args/kwargs (arrays, dask or otherwise)](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/random.py#L964) | still there |
| 2025 | 0.84 | [We can do better, but not high priority](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_reductions.py#L1483) | still there |
| 2025 | 0.83 | [At this point we could verify if we're dealing with a very](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/io/parquet.py#L1029) | still there |
| 2025 | 0.82 | [Handle alignment?](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_collection.py#L6177) | still there |
| 2025 | 0.82 | [We can do better in some cases](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_reductions.py#L1348) | still there |
| 2025 | 0.81 | [duplicated columns](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_collection.py#L3912) | still there |
| 2025 | 0.80 | [capture index-merge as well](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/dataframe/dask_expr/_merge.py#L296) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.46 | [This should probably be a dedicated expression](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_expr.py#L136) | still there |
| 2025 | 0.47 | [Highlevelgraph :(](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_blockwise.py#L191) | still there |
| 2025 | 0.49 | [this class is a confusing crutch to pass arguments to the](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_blockwise.py#L175) | still there |
| 2025 | 0.50 | [Fix this, this is ugly and should happen later](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/random.py#L539) | still there |
| 2025 | 0.52 | [This needs something like what we have in DataFrame land with ACA](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_reductions.py#L22) | still there |
| 2025 | 0.56 | [Need asarray for this](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_collection.py#L919) | still there |
| 2025 | 0.57 | [Needs more IO Stuff](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_reductions.py#L166) | still there |
| 2025 | 0.57 | [Not done yet, but needed for assert_eq to identify us as an Array](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_collection.py#L315) | still there |
| 2025 | 0.57 | [We should probably go through blockwise here](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/array/_array_expr/_collection.py#L927) | still there |
| 2025 | 0.58 | [Make this also go away](https://github.com/dask/dask/blob/17a245a70596f2d3b78cdc8fea20d2dd3ca838d5/dask/delayed.py#L181) | still there |
### apache/airflow

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.97 | [is not reachable as its connection is currently being updated".](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/amazon/src/airflow/providers/amazon/aws/hooks/emr.py#L362) | still there |
| 2025 | 0.93 | [TaskSDK: move this type change into BaseExecutor](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/amazon/src/airflow/providers/amazon/aws/executors/batch/batch_executor.py#L110) | **resolved** |
| 2025 | 0.92 | [TaskSDK: move this type change into BaseExecutor](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/amazon/src/airflow/providers/amazon/aws/executors/aws_lambda/lambda_executor.py#L74) | **resolved** |
| 2025 | 0.92 | [TaskSDK: move this type change into BaseExecutor](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/amazon/src/airflow/providers/amazon/aws/executors/ecs/ecs_executor.py#L105) | **resolved** |
| 2025 | 0.91 | [AIP-72 handle populating tokens once https://github.com/apache/airflow/issues/45107 is han](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/cncf/kubernetes/src/airflow/providers/cncf/kubernetes/executors/kubernetes_executor.py#L302) | still there |
| 2025 | 0.91 | [TaskSDK: move this type change into BaseExecutor](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/cncf/kubernetes/src/airflow/providers/cncf/kubernetes/executors/kubernetes_executor.py#L151) | **resolved** |
| 2025 | 0.90 | [When merged this needs updating to the actually supported version](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/amazon/tests/unit/amazon/aws/executors/ecs/test_ecs_executor.py#L1349) | still there |
| 2025 | 0.90 | [(#54350): do not use connection.extra_dejson until it's fixed in Airflow otherwise expect:](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/microsoft/azure/src/airflow/providers/microsoft/azure/hooks/msgraph.py#L254) | **resolved** |
| 2025 | 0.90 | [Consider these env variables jointly in task sdk together with task_sdk/src/airflow/sdk/ap](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/edge3/src/airflow/providers/edge3/cli/api_client.py#L55) | still there |
| 2025 | 0.89 | [Potential performance issue, converted setup_class to a setup_connections function level f](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/dbt/cloud/tests/unit/dbt/cloud/hooks/test_dbt.py#L165) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.07 | [We should bring it back when ray is supported on Python 3.13](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/airflow-core/tests/unit/serialization/test_dag_serialization.py#L1322) | still there |
| 2025 | 0.21 | [Remove this flag once providers depend on Airflow 3.0](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/celery/src/airflow/providers/celery/executors/celery_kubernetes_executor.py#L62) | still there |
| 2025 | 0.21 | [Remove this once providers depend on Airflow 3.0](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/celery/src/airflow/providers/celery/executors/celery_kubernetes_executor.py#L193) | still there |
| 2025 | 0.22 | [Remove this when min airflow version is 2.10.0 for standard provider](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/standard/src/airflow/providers/standard/sensors/time.py#L32) | **resolved** |
| 2025 | 0.25 | [Remove this when min airflow version is 2.10.0 for standard provider](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/standard/src/airflow/providers/standard/sensors/date_time.py#L31) | **resolved** |
| 2025 | 0.26 | [Remove this when min airflow version is 2.10.0 for standard provider](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/standard/src/airflow/providers/standard/sensors/filesystem.py#L36) | **resolved** |
| 2025 | 0.28 | [Remove this attribute once providers rely on Airflow >=3.0.0](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/cncf/kubernetes/src/airflow/providers/cncf/kubernetes/executors/local_kubernetes_executor.py#L55) | still there |
| 2025 | 0.28 | [remove me when we get rid of the dependency](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/dev/breeze/src/airflow_breeze/utils/selective_checks.py#L573) | still there |
| 2025 | 0.28 | [remove me when we get rid of the dependency](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/dev/breeze/src/airflow_breeze/utils/selective_checks.py#L563) | still there |
| 2025 | 0.30 | [Remove this after minimum Airflow version is 3.0](https://github.com/apache/airflow/blob/c846f6f27fe97ebd00cc0a13cf7ee59f1020877b/providers/ssh/src/airflow/providers/ssh/operators/ssh.py#L174) | still there |
### ansible/ansible

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.86 | [Consolidate with the other methods calling set_*_if_different method, this is inefficient.](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/modules/copy.py#L346) | still there |
| 2025 | 0.85 | [reasearch how feasible it is to implement the above](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/modules/dnf.py#L743) | **resolved** |
| 2025 | 0.84 | [resolve conflict with check mode, added manually below](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/cli/pull.py#L137) | still there |
| 2025 | 0.81 | [consider pinning the twine requirement and its dependencies](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/packaging/release.py#L1309) | still there |
| 2025 | 0.81 | [consider pinning the build requirement and its dependencies](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/packaging/release.py#L1211) | still there |
| 2025 | 0.80 | [split distro file parsing into its own module or class](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/module_utils/facts/system/distribution.py#L210) | still there |
| 2025 | 0.79 | [mounts isn't exactly hardware](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/module_utils/facts/hardware/base.py#L52) | still there |
| 2025 | 0.79 | [consider pinning the ansible requirements and dependencies](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/packaging/release.py#L1154) | still there |
| 2025 | 0.79 | [reasearch how feasible it is to implement the above](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/modules/dnf5.py#L727) | **resolved** |
| 2025 | 0.78 | [enforce keys are strings](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/plugins/inventory/ini.py#L357) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.15 | [Inspect and remove all calls to this function in 2.24](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/module_utils/_internal/_no_six.py#L80) | still there |
| 2025 | 0.44 | [docker - remove these](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/playbook/play_context.py#L93) | still there |
| 2025 | 0.46 | [define and document a pass-through value_type (None, 'raw', 'object', '', ...) and then de](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/config/manager.py#L219) | still there |
| 2025 | 0.54 | [deprecate and remove, most plugins that needed this don't use this facility anymore](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/plugins/__init__.py#L153) | still there |
| 2025 | 0.55 | [object identity/singleton-ness does not appear to survive pickle roundtrip (eg, copy.copy,](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/utils/singleton.py#L15) | still there |
| 2025 | 0.57 | [avoid `SKIPPED` notifications for inherited tests with no data](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/test/units/utils/test_datatag.py#L73) | still there |
| 2025 | 0.59 | [normalize `failed` to a bool, warn if the action/module used non-bool](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/executor/task_executor.py#L355) | **resolved** |
| 2025 | 0.59 | [normalize `failed` to a bool, warn if the action/module used non-bool](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/executor/task_executor.py#L143) | **resolved** |
| 2025 | 0.59 | [normalize `failed` to a bool, warn if the action/module used non-bool](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/lib/ansible/executor/task_executor.py#L116) | **resolved** |
| 2025 | 0.63 | [this test should really be using a shared collection loader fixture, but this fixes an "in](https://github.com/ansible/ansible/blob/730af3239d2287b0add73e0f9119871320f60377/test/units/_internal/templating/test_templar.py#L872) | still there |
### saltstack/salt

Most at risk of rotting (the model's top warnings):

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.90 | [Force un-install for now](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/pkg/upgrade/systemd/conftest.py#L42) | still there |
| 2025 | 0.90 | [extra is never None](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/_logging/impl.py#L282) | still there |
| 2025 | 0.89 | [we don't return a future anymore, this needs a different way of testing.](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/unit/transport/test_tcp.py#L287) | **resolved** |
| 2025 | 0.87 | [This is only used by syndic](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/minion.py#L1675) | still there |
| 2025 | 0.85 | [This should no longer be neede because of using salt_cli.run.](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/integration/loader/test_ext_grains.py#L11) | still there |
| 2025 | 0.85 | [This is only used by syndic and should be moved to the Syndic class.](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/minion.py#L2415) | still there |
| 2025 | 0.85 | [Linter failure needs to be addressed E1126](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/integration/states/test_idem.py#L53) | still there |
| 2025 | 0.84 | [This does not make sense](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/minion.py#L3782) | still there |
| 2025 | 0.84 | [The sync flag is only called with sync=False. Which also means](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/minion.py#L2416) | still there |
| 2025 | 0.84 | [Maybe need to move that ^^^^ to a salt util](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/runners/manage.py#L792) | still there |

Least at risk:

| Replayed in | Risk | TODO | What happened |
|---|---|---|---|
| 2025 | 0.63 | [But maybe that's done elsewhere, hopefully in self.salt_pkgs](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/support/pkg.py#L869) | still there |
| 2025 | 0.64 | [There's probably something I should put in here to say what version](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/support/pkg.py#L868) | still there |
| 2025 | 0.73 | [This module checking should be a separate integration in](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/pkg/upgrade/test_salt_upgrade.py#L150) | **resolved** |
| 2025 | 0.74 | [This should be temporary. See also a similar thing happening](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/support/pkg.py#L954) | **resolved** |
| 2025 | 0.74 | [This should be temporary. See also a similar thing happening](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/support/pkg.py#L483) | **resolved** |
| 2025 | 0.74 | [Similar to tests/support/win_installer.py](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/salt/runners/manage.py#L791) | still there |
| 2025 | 0.75 | [The gpg module needs a gpg binary on](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/pkg/upgrade/test_salt_upgrade.py#L153) | **resolved** |
| 2025 | 0.76 | [Come up with a faster way of knowing whne we are ready.](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/pkg/upgrade/test_salt_upgrade.py#L81) | **resolved** |
| 2025 | 0.78 | [The gpg module needs a gpg binary on](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/pytests/pkg/downgrade/test_salt_downgrade.py#L66) | **resolved** |
| 2025 | 0.78 | [Add install path to cli_scripts.generate_scripts?](https://github.com/saltstack/salt/blob/904d08b6ad311fd95c75004fbc3dab2b241f9ce6/tests/support/pkg.py#L1604) | still there |
