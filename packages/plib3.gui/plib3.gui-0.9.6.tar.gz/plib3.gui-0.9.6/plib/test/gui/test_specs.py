#!/usr/bin/env python3
"""
TEST.GUI.TEST_SPECS.PY -- test script for module SPECS, sub-package GUI of package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the PLIB3.GUI.SPECS module.
"""

import unittest
import types

try:
    from plib.gui import specs

except ValueError:
    # No GUI toolkit was found -- skip test
    specs = None
    print("GUI toolkit not found, skipping plib.gui test cases.")

if specs is not None:
    
    specnames = [fname for fname in dir(specs) if fname.startswith('get_')]
    
    dummy_str = 'spectest'
    dummy_int = 0
    dummy_bool = False
    dummy_list = []
    dummy_func = lambda: None
    
    argmap = {
        'name': dummy_str,
        'label': dummy_str,
        'caption': dummy_str,
        'text': dummy_str,
        'pxname': dummy_str,
        'action': dummy_int,
        'align': dummy_int,
        'layout': dummy_int,
        'expand': dummy_bool,
        'scrolling': dummy_bool,
        'labels': dummy_list,
        'items': dummy_list,
        'tabs': dummy_list,
        'contents': dummy_list,
        'target': dummy_str,
        'width': dummy_int,
        'key': dummy_func
    }
    
    
    def spec(fname, include_defaults=False):
        specfn = getattr(specs, fname)
        code = specfn.__code__
        argnames = code.co_varnames[:code.co_argcount]
        defaultindex = len(argnames) - len(specfn.__defaults__ or list())
        args = tuple([argmap[argname] for argname in argnames[:defaultindex]])
        if include_defaults:
            kwargs = dict([(argname, argmap[argname]) for argname in argnames[defaultindex:]])
        else:
            kwargs = {}
        return specfn(*args, **kwargs)
    
    
    def spec_format_ok(specobj):
        return (isinstance(specobj, tuple)
                and (len(specobj) == 4)
                and (isinstance(specobj[0], types.FunctionType) or isinstance(specobj[0], list))
                and isinstance(specobj[1], tuple)
                and isinstance(specobj[2], dict)
                and isinstance(specobj[3], str))
    
    
    class Test_specs(unittest.TestCase):
        
        def test_formats(self):
            for specname in specnames:
                self.failUnless(spec_format_ok(spec(specname)))
                self.failUnless(spec_format_ok(spec(specname, include_defaults=True)))


if __name__ == '__main__':
    unittest.main()
