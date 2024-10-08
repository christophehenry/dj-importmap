from dj_importmap.settings import INSTALLED_APPS

# dj-importmap: HTML importmaps like a boss!

`dj-importmaps` is designed to help you declare your [`importmap`s](https://developer.mozilla.org/fr/docs/Web/HTML/Element/script/type/importmap)
in a djangonic way.

## Show me an example!

For instance, the following:

```python
# importmaps.py in one of your Django apps
from importmap import static

importmaps = {
    # From your static files
    "SearchComponent": static("js/search-component.js"),
    # Or declare directly from a CDN
    "StimulusJS": "https://unpkg.com/stimulus@3.2.2/dist/stimulus.umd.js"
}
```

This will generate the following:

```html
<script type="importmap">
  {
    "imports": {
        "SearchComponent": "/static/js/search-component.js",
        "StimulusJS": "https://unpkg.com/stimulus@3.2.2/dist/stimulus.js"
    }
  }
</script>

```

And now, you can use JS modules like nothing:

```js
import {Controller, Application} from "StimulusJS"
import * as Search from "SearchComponent"

export default class {
    // ...
}
```

## Cool! How do I use it?

1. Install from PyPI
    ```shell
    pip install dj-importmap
    ```

2. Add to your `INSTALLED_APPS:
    ```python
    INSTALLED_APPS = [
        # ...
        "importmap"
        # ...
    ]
    ```

3. Create a `importmaps.py` next to your root `urls.py` or in any of your Django app:
    ```python
    importmaps = {
        # ...
    }
    ```

4. Add `{% importmap %}` to you template:
    ```html
    {% load importmap %}
    <!doctype html>
    <html lang="fr" data-fr-scheme="light">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>…</title>
      <!-- This must be placed before the very first <script> in order to work -->
      {% importmap %}
    </head>
    </html>
    ```
You're good to go!

## Advanced usage

### Per-app `importmaps.py`

You can declare an different `importmap` for your whole Django project as well as for each application. By default,
when you call `{% importmap %}` in a template, `dj-importmap` will merge them all in the order the app were declared in
`INSTALLED_APPS`, the latter take precedence over the former.

If you want to use a `importmaps.py` declared in a spcific app, you can use `{% importmap "app_name" %}` where
`app_name` corresponds to the `AppConfig.name` declared in your Django's app `apps.py`. In this case, `{% importmap %}`
will merge the app's `importmaps.py` to the project `importmaps.py`, if exists.

`dj-importmap` expects to find the project's `importmaps.py` next to the project's `urls.py`, as declared in
`settings.ROOT_URLCONF`.

Alternatively, if `settings.ROOT_IMPORTMAPCONF` is declared and points to a valid Python module, `dj-importmap` will
source that one as the project's root importmap.

### Additionnal HTML attribute to the generated `<script>`

`{% importmap %}` accepts kwargs to let you add arbitrary HTML attributes to the generated `<script>`:

```django
{% importmap defer="true" %}
<!-- Using attributes with chars unauthorized in Django templates -->
{% importmap defer="true" "yes" as "data-is-cool" %}
<!-- Attribute without value -->
{% importmap "defer" "yes" as "data-is-cool" %}
```

**Note**: trying to specify an HTML attribute with no value as the first argument of `{% importmap %}` creates an
ambiguity with the optionam app name. In this case, `{% importmap %}` will raise a `TemplateSyntaxError`.
`{% importmap %}` offer the possibility to suppress this ambiguity by setting a series of dashes as its first
argument:

```django
<!-- TemplateSyntaxError: ambiguity -->
`{% importmap "defer" %}`
<!-- Ok -->
{% importmap "--" "defer" %}
```
