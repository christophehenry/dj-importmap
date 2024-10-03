import json
import re
from typing import Optional, Any, Tuple

from django.template import Library, TemplateSyntaxError
from django.template.base import token_kwargs, Node
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from importmap import importmaps

register = Library()


@register.tag
def importmap(parser, token):
    return ImportMapNode(parser, token)


class ImportMapNode(Node):
    def __init__(self, parser, token):
        self.parser = parser
        self.token = token

    def render(self, context):
        bits = self.token.split_contents()[1:]

        if len(bits) == 0:
            return self._render()

        appname = None
        html_params = []

        enumarator = enumerate(bits)
        for i, bit in enumarator:
            k, v, bits_consummed = self._parse_kwarg(context, bits, i)
            if bits_consummed == 0:
                appname = self.parser.compile_filter(bit).resolve(context)
                continue

            if k == "type":
                raise TemplateSyntaxError(
                    "Passing 'type' as an additionnal HTML attribute is disallowed"
                )

            [next(enumarator, None) for _ in range(1, bits_consummed)]
            html_params.append(f'{k}="{v}"' if v is not None else f"{k}")

        if appname is not None and re.compile(r"-+").match(str(appname)):
            appname = None

        from django.apps import apps

        if appname and appname not in apps.app_configs:
            raise TemplateSyntaxError(
                f"Unknown app name {appname}; you may be trying to ambigiously pass "
                'an HTML attribute. Please add "--" before HTML attributes to '
                "disambiguate."
            )

        return self._render(appname, *html_params)

    def _render(self, appname: Optional[str] = None, *html_params):
        imports = importmaps.get_for_app(appname) if appname else dict(importmaps)

        return format_html(
            '<script type="importmap"{}>{}</script>',
            mark_safe(" ".join(["", *html_params]) if html_params else ""),
            mark_safe(json.dumps({"imports": imports})),
        )

    def _parse_kwarg(self, context, bits, idx) -> Tuple[Optional[str], Any, int]:
        result = token_kwargs([bits[idx]], self.parser)
        if result:
            # case 'k="v"'
            k, v = list(result.items())[0]
            return k, v.resolve(context), 1

        result = token_kwargs(bits[idx : idx + 3], self.parser, support_legacy=True)
        if result:
            # case '"v" as "k"'
            k, v = list(result.items())[0]
            return self.parser.compile_filter(k).resolve(context), v.resolve(context), 3

        # case "v"
        if idx > 0:
            return self.parser.compile_filter(bits[idx]).resolve(context), None, 1

        # appname case
        return None, None, 0
