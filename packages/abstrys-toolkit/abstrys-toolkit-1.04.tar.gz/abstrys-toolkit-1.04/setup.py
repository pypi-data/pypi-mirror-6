#!/usr/bin/env python
from distutils.core import setup

script_names = [
    'scripts/cleanjson',
    'scripts/clinks',
    'scripts/fix_filenames',
    'scripts/rompy',
    'scripts/s3del',
    'scripts/s3lod',
    'scripts/s3pub',
    'scripts/snippetize',
    'scripts/srep', ]


long_desc = """
abstrys-toolkit
===============

Useful command-line tools and scripts. Designed for tech writers, usable
by anyone.

Included in the toolkit are the following tools:

-  **cleanjson** - cleans up messy json
-  **clinks** - check links in HTML files.
-  **fix\_filenames** - modifies filenames on the system to snake\_case
-  **rompy** - Runs an arbitrary command when a tracked file's modification
               time changes
-  **s3del** - Deletes Amazon S3 keys or buckets
-  **s3lod** - Lists or downloads the contents of Amazon S3 buckets
-  **s3pub** - Publishes (upload and make public) any file(s) from the
               local system to an Amazon S3 bucket.
-  **srep** - search and replace in files given a filespec (either file names
              or a glob, ex. \*.xml)
-  **snippetize** - cut a file into snippets (or remove snippet markers)

License
-------

This software is provided under the `BSD
3-Clause <http://opensource.org/licenses/BSD-3-Clause>`__ license. See
the `LICENSE
file <https://github.com/Abstrys/abstrys-toolkit/blob/master/LICENSE>`__
for more details.

For more information
--------------------

Contact
`eron@abstrys.com <mailto:eron@abstrys.com?Subject=abstrys-toolkit>`__."""

setup(name='abstrys-toolkit',
      description="""Useful command-line tools and scripts, designed for
      technical writing and publication.""",
      version='1.04',
      requires=['json', 'boto', 'PyYAML', 'httplib2'],
      scripts=script_names,
      author='Eron Hennessey',
      author_email='eron@abstrys.com',
      url='https://github.com/Abstrys/abstrys-toolkit',
      )
