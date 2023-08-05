# coding: utf-8
from unittest import main, TestCase
from django.template import Context
from django.template.loader import render_to_string, get_template_from_string
from mock import patch, MagicMock
from static_precompiler.compilers.coffeescript import CoffeeScript
from static_precompiler.exceptions import StaticCompilationError


class CoffeeScriptTestCase(TestCase):

    @staticmethod
    def clean_javascript(js):
        """ Remove comments and all blank lines. """
        return "\n".join(
            line for line in js.split("\n") if line.strip() and not line.startswith("//")
        )

    def test_is_supported(self):
        compiler = CoffeeScript()
        self.assertEqual(compiler.is_supported("dummy"), False)
        self.assertEqual(compiler.is_supported("dummy.coffee"), True)

    def test_get_output_filename(self):
        compiler = CoffeeScript()
        self.assertEqual(compiler.get_output_filename("dummy.coffee"), "dummy.js")
        self.assertEqual(
            compiler.get_output_filename("dummy.coffee.coffee"),
            "dummy.coffee.js"
        )

    def test_compile_file(self):
        compiler = CoffeeScript()

        self.assertEqual(
            self.clean_javascript(compiler.compile_file("scripts/test.coffee")),
            """(function() {\n  console.log("Hello, World!");\n}).call(this);"""
        )

    def test_compile_source(self):
        compiler = CoffeeScript()

        self.assertEqual(
            self.clean_javascript(compiler.compile_source('console.log "Hello, World!"')),
            """(function() {\n  console.log("Hello, World!");\n}).call(this);"""
        )

        self.assertRaises(
            StaticCompilationError,
            lambda: compiler.compile_source('console.log "Hello, World!')
        )

        # Test non-ascii
        self.assertEqual(
            self.clean_javascript(compiler.compile_source('console.log "Привет, Мир!"')),
            """(function() {\n  console.log("Привет, Мир!");\n}).call(this);"""
        )

    def test_coffessecript_templatetag(self):
        template = get_template_from_string("""{% load coffeescript %}{% coffeescript "dummy.coffee" %}""")
        with patch("static_precompiler.templatetags.coffeescript.compiler") as mocked_compiler:
            mocked_compiler.compile = MagicMock(return_value="dummy.js")
            self.assertEqual(
                template.render(Context({})),
                "dummy.js",
            )

    def test_inlinecoffessecript_templatetag(self):
        template = get_template_from_string("""{% load coffeescript %}{% inlinecoffeescript %}source{% endinlinecoffeescript %}""")
        with patch("static_precompiler.templatetags.coffeescript.InlineCoffeescriptNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )

if __name__ == '__main__':
    main()
