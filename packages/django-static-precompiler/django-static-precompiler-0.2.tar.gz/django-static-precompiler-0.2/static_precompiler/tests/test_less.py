# coding: utf-8
from unittest import main, TestCase
from django.template import Context
from django.template.loader import get_template_from_string
from mock import patch, MagicMock
from static_precompiler.compilers import LESS
from static_precompiler.exceptions import StaticCompilationError
from static_precompiler.settings import STATIC_ROOT
import os


class LESSTestCase(TestCase):

    def test_is_supported(self):
        compiler = LESS()
        self.assertEqual(compiler.is_supported("dummy"), False)
        self.assertEqual(compiler.is_supported("dummy.less"), True)

    def test_get_output_filename(self):
        compiler = LESS()
        self.assertEqual(compiler.get_output_filename("dummy.less"), "dummy.css")
        self.assertEqual(
            compiler.get_output_filename("dummy.less.less"),
            "dummy.less.css"
        )

    def test_compile_file(self):
        compiler = LESS()

        self.assertEqual(
            compiler.compile_file("styles/test.less"),
            """p {
  font-size: 15px;
}
p a {
  color: red;
}
h1 {
  color: blue;
}
"""
        )

    def test_compile_source(self):
        compiler = LESS()

        self.assertEqual(
            compiler.compile_source("p {font-size: 15px; a {color: red;}}"),
            "p {\n  font-size: 15px;\n}\np a {\n  color: red;\n}\n"
        )

        self.assertRaises(
            StaticCompilationError,
            lambda: compiler.compile_source('invalid syntax')
        )

        # Test non-ascii
        NON_ASCII = """.external_link:first-child:before {
  content: "Zobacz także:";
  background: url(картинка.png);
}
"""
        self.assertEqual(
            compiler.compile_source(NON_ASCII),
            NON_ASCII
        )

    def test_postprocesss(self):
        compiler = LESS()
        with patch("static_precompiler.compilers.less.convert_urls") as mocked_convert_urls:
            mocked_convert_urls.return_value = "spam"
            self.assertEqual(compiler.postprocess("ham", "eggs"), "spam")
            mocked_convert_urls.assert_called_with("ham", "eggs")

    def test_find_imports(self):
        compiler = LESS()
        source = """
@import "foo.css", ;
@import " ";
@import "foo.less";
@import (less) "bar";
@import "foo";
@import "foo.css";
@import "foo" screen;
@import "http://foo.com/bar";
@import url(foo);
@import "rounded-corners", "text-shadow";
"""
        expected = [
            "bar",
            "foo",
            "foo.less",
            "rounded-corners",
            "text-shadow",
        ]
        self.assertEqual(
            compiler.find_imports(source),
            expected
        )

    def test_locate_imported_file(self):
        compiler = LESS()
        with patch("os.path.exists") as mocked_os_path_exist:

            existing_files = set()
            for f in ("A/B.less", "D.less"):
                existing_files.add(os.path.join(STATIC_ROOT, f))

            mocked_os_path_exist.side_effect = lambda x: x in existing_files

            self.assertEqual(
                compiler.locate_imported_file("A", "B.less"),
                "A/B.less"
            )
            self.assertEqual(
                compiler.locate_imported_file("E", "../D"),
                "D.less"
            )
            self.assertEqual(
                compiler.locate_imported_file("E", "../A/B.less"),
                "A/B.less"
            )
            self.assertEqual(
                compiler.locate_imported_file("", "D.less"),
                "D.less"
            )
            self.assertRaises(
                StaticCompilationError,
                lambda: compiler.locate_imported_file("", "Z.less")
            )

    def test_find_dependencies(self):
        compiler = LESS()
        files = {
            "A.less": "@import 'B/C.less';",
            "B/C.less": "@import '../E';",
            "E.less": "p {color: red;}",
        }
        compiler.get_source = MagicMock(side_effect=lambda x: files[x])

        existing_files = set()
        for f in files:
            existing_files.add(os.path.join(STATIC_ROOT, f))

        with patch("os.path.exists") as mocked_os_path_exist:
            mocked_os_path_exist.side_effect = lambda x: x in existing_files

            self.assertEqual(
                compiler.find_dependencies("A.less"),
                ["B/C.less", "E.less"]
            )
            self.assertEqual(
                compiler.find_dependencies("B/C.less"),
                ["E.less"]
            )
            self.assertEqual(
                compiler.find_dependencies("E.less"),
                []
            )

    def test_less_templatetag(self):
        template = get_template_from_string("""{% load less %}{% less "dummy.less" %}""")
        with patch("static_precompiler.templatetags.less.compiler") as mocked_compiler:
            mocked_compiler.compile = MagicMock(return_value="dummy.css")
            self.assertEqual(
                template.render(Context({})),
                "dummy.css",
            )

    def test_inlineless_templatetag(self):
        template = get_template_from_string("""{% load less %}{% inlineless %}source{% endinlineless %}""")
        with patch("static_precompiler.templatetags.less.InlineLESSNode.compiler") as mocked_compiler:
            mocked_compiler.compile_source = MagicMock(return_value="compiled")
            self.assertEqual(
                template.render(Context({})),
                "compiled",
            )


if __name__ == '__main__':
    main()
