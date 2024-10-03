import json
from django.template import Context, Template, TemplateSyntaxError
from django.test import LiveServerTestCase

from importmap import importmaps


class ImportmapTestCase(LiveServerTestCase):
    def test_get_importmaps(self):
        self.assertEqual(
            {
                "DoesSomethingElseComponent": "/static/js/does-something-else.js",
                "DoesSomethingComponent": "https://example.com/does-something.js",
            },
            dict(importmaps),
        )

    def test_rendering(self):
        self.assertEqual(
            '<script type="importmap">{"imports": {'
            '"DoesSomethingComponent": "https://example.com/does-something.js", '
            '"DoesSomethingElseComponent": "/static/js/does-something-else.js"'
            "}}</script>",
            Template("{% load importmap %}{% importmap %}").render(Context({})),
        )

    def test_kwarg(self):
        case = '"testapp"'
        with self.subTest(case):
            self.assertEqual(
                f'<script type="importmap">{{"imports": {json.dumps(importmaps.get_for_app("testapp"))}}}</script>',
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({})),
            )

        case = '"defer"'
        with self.subTest(case):
            with self.assertRaises(TemplateSyntaxError):
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({}))

        case = '"--" "defer"'
        with self.subTest(case):
            self.assertEqual(
                f'<script type="importmap" defer>{{"imports": {json.dumps(dict(importmaps))}}}</script>',
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({})),
            )

        case = '"defer" nonce="??nq(C?[i4=yH_xt[hE4nE@V:7jw{["'
        with self.subTest(case):
            with self.assertRaises(TemplateSyntaxError):
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({}))

        case = '"--" "defer" nonce="??nq(C?[i4=yH_xt[hE4nE@V:7jw{["'
        with self.subTest(case):
            self.assertEqual(
                '<script type="importmap" defer nonce="??nq(C?[i4=yH_xt[hE4nE@V:7jw{[">'
                f'{{"imports": {json.dumps(dict(importmaps))}}}</script>',
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({})),
            )

        case = '"testapp" "defer" nonce="??nq(C?[i4=yH_xt[hE4nE@V:7jw{["'
        with self.subTest(case):
            self.assertEqual(
                '<script type="importmap" defer nonce="??nq(C?[i4=yH_xt[hE4nE@V:7jw{[">'
                f'{{"imports": {json.dumps(dict(importmaps))}}}</script>',
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({})),
            )

        case = '"--" "defer" "true" as "data-test"'
        with self.subTest(case):
            self.assertEqual(
                '<script type="importmap" defer data-test="true">'
                f'{{"imports": {json.dumps(dict(importmaps))}}}</script>',
                Template(f"{{% load importmap %}}{{% importmap {case} %}}").render(Context({})),
            )
