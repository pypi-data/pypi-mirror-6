from unittest import TestCase
from pyjx.translate import translate, get_libs_as_js
import PyV8

APP_TEMPLATE = """
var $wnd = new Object();
$wnd.document = new Object();
var $doc = $wnd.document;
var $pyjs = new Object();
var $p = null;
$pyjs.__modules__ = {};
$pyjs.modules = {};
$pyjs.modules_hash = {};
$pyjs.loaded_modules = {};
$pyjs.options = new Object();
$pyjs.options.set_all = function (v) {
    $pyjs.options.arg_ignore = v;
    $pyjs.options.arg_count = v;
    $pyjs.options.arg_is_instance = v;
    $pyjs.options.arg_instance_type = v;
    $pyjs.options.arg_kwarg_dup = v;
    $pyjs.options.arg_kwarg_unexpected_keyword = v;
    $pyjs.options.arg_kwarg_multiple_values = v;
};
$pyjs.options.set_all(true);
$pyjs.trackstack = [];
$pyjs.track = {module:'__main__', lineno: 1};
$pyjs.trackstack.push($pyjs.track);
$pyjs.__last_exception_stack__ = null;
$pyjs.__last_exception__ = null;
$pyjs.platform = 'pyv8';
$pyjs.loadpath = './';
"""
LOADPYJSLIB="""
$p = $pyjs.loaded_modules['pyjslib'];
$p('pyjslib');
$pyjs.__modules__.pyjslib = $p['pyjslib'];
$pyjs.loaded_modules['pyjslib'].___import___('%(app_name)s', '%(app_name)s', '__main__');
"""

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__)+'../../../pyjs/')
pyjslibpath = os.path.join(BASE_DIR, 'builtin/pyjslib.py')

class V8TestCase(TestCase):
    includes = []
    translate = []

    @classmethod
    def setUpClass(cls):
        cls.includes_src = get_libs_as_js()
        for f in cls.includes:
            with open(f) as fd:
                cls.includes_src += fd.read() + '\n'
        for f in cls.translate:
            with open(f) as fd:
                cls.includes_src += fd.read() + '\n'

    def setUp(self):
        self.ctx = PyV8.JSContext()
        self.ctx.enter()
        if self.includes_src:
            self.eval(self.includes_src)

    def translate_eval(self, pysrc, *valnames):
        if pysrc[:-1] != '\n':
            pysrc += '\n'
        self.eval(translate(pysrc,'mod'))
        mod = self.ctx.locals['$pyjs']['loaded_modules']['mod']
        mod()
        result = [getattr(mod, valname) for valname in valnames]
        if len(valnames) == 1:
            return result[0]
        return result
    te = translate_eval

    def eval(self, js):
        return self.ctx.eval(js)

    def assertMROs(self, pyobj, jsobj):
        self.assertObjectNamesEqual(pyobj.__mro__, jsobj+'.__mro__')

    def assertObjectNamesEqual(self, pyobjects, jsobjects):
        pynames = [i.__name__ for i in pyobjects]
        result = self.eval(jsobjects)
        jsnames = [str(i.__name__) for i in result]
        self.assertSequenceEqual(pynames, jsnames)

    def assertJSArrayEqual(self, jsarray1, jsarray2):
        array1 = self.eval(jsarray1)
        array2 = self.eval(jsarray2)
        self.assertSequenceEqual(list(array1), list(array2))
