from pyjs.translator_proto import *
from os.path import join, dirname, abspath

builddir = abspath(join(dirname(__file__),'../../pyjs/'))
app_library_dirs = [
    join(builddir, "builtin"),
    join(builddir, "builtin/public/"),
    join(builddir, "lib")
]

def get_libs_as_js():
    parser = PlatformParser(compiler, verbose=False)
    parser.setPlatform("pyv8")
    app_translator = AppTranslator(
            compiler, app_library_dirs, parser,
            verbose = False,
            debug = False,
            print_statements = False,
            function_argument_checking = False,
            attribute_checking = False,
            source_tracking = False,
            line_tracking = False,
            store_source = False,
    )
    app_libs,_ = app_translator.translate(None, library_modules=['_pyjs.js', 'sys', 'pyjslib'])

    txt = """
var $wnd = new Object();
$wnd.document = new Object();
var $doc = $wnd.document;
var $pyjs = new Object();
var $p = null, pyjslib, sys;
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
    txt += app_libs
    txt += """
$p = $pyjs['loaded_modules']['pyjslib'];
$p('pyjslib');
$pyjs['__modules__']['pyjslib'] = $p;
//$p = $pyjs['loaded_modules']['pyjslib']('pyjslib');
//$p = $pyjs['loaded_modules']['pyjslib'];
//$p('pyjslib');
//$pyjs['__modules__']['pyjslib'] = $p;
    """
    return txt

def translate(py_input, module, js_output=None):
    kw = dict(all_compile_options,
            debug=False,
            line_tracking=False,
            source_tracking=False,
            attribute_checking=False,
            number_classes=False,
            store_source=False)

    tree = compiler.parse(py_input)

    output = js_output
    if not js_output:
        output = StringIO()

    t = Translator(compiler, 'mod', 'foo.py', py_input, tree, output, **kw)

    if not js_output:
        return output.getvalue()
