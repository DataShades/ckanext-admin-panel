import re
from urllib.parse import urljoin

import pytest

from ckan.common import config


_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\" )]+)['\"]?\s*\)")
_FONT_CSS_URL = "/catalog/admin_panel/fonts/fonts.css"


def _backend_path(url):
    root_path = config["ckan.root_path"].replace("{{LANG}}", "").rstrip("/")
    assert url.startswith(root_path + "/")
    return url.removeprefix(root_path)


@pytest.mark.ckan_config("ckan.root_path", "/catalog")
def test_montserrat_fonts_are_local(app, sysadmin):
    response = app.get("/user/login", status=200)
    admin_page = app.get(
        "/admin-panel/config",
        extra_environ={"REMOTE_USER": sysadmin["name"].encode("ascii")},
        status=200,
    )

    assert f'href="{_FONT_CSS_URL}"' in response.text
    assert f'href="{_FONT_CSS_URL}"' in admin_page.text
    assert "fonts.googleapis.com" not in response.text

    admin_css_url = next(
        url
        for url in re.findall(r'href="([^"]+\.css)"', response.text)
        if url.endswith("-admin_panel.css")
    )
    admin_css = app.get(_backend_path(admin_css_url), status=200)
    assert 'font-family:"Montserrat",sans-serif' in admin_css.text
    assert "fonts.googleapis.com" not in admin_css.text

    stylesheet = app.get(_backend_path(_FONT_CSS_URL), status=200)
    assert stylesheet.text.count("@font-face") == 10

    for asset_url in _CSS_URL.findall(stylesheet.text):
        assert not asset_url.startswith(("http://", "https://", "//"))
        app.get(
            _backend_path(urljoin(_FONT_CSS_URL, asset_url)),
            status=200,
        )
