import doctest
import os

import manuel.codeblock
import manuel.doctest
import manuel.testing

from . import testcode
from . import unicode_output


def get_doctest_suite(docnames):
    """Return the doctest suite for specified docnames."""

    docnames = [
        os.path.join(
            os.getcwd(),
            doc,
        )
        for doc in docnames
    ]

    m = manuel.doctest.Manuel(
        parser=unicode_output.PermissiveUnicodeDocTestParser(),
        optionflags=doctest.ELLIPSIS,
    )
    m += manuel.codeblock.Manuel()
    m += testcode.Manuel()

    return manuel.testing.TestSuite(
        m,
        *docnames
    )
