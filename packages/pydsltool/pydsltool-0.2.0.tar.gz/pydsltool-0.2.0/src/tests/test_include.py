
import dsltool
from inspect import cleandoc

import pytest

#
# DSL Objects
#

class GrandchildDsl(object):
    grandchild_var = None

class IncludedDsl(object):
    works = False

class BaseDsl(object):
    
    not_included = None
    included_foo = None
    
    included_dsl = IncludedDsl



def test_include_0a0():
    dsl_contents = cleandoc('''
        not_included = True
        include_file('included.pydsl')
    ''')
    
    result = dsltool.parse_dsl(dsl_contents, BaseDsl, __file__)
    assert result.not_included == True
    assert result.included_foo == True
    assert result.included_dsl.works == True

