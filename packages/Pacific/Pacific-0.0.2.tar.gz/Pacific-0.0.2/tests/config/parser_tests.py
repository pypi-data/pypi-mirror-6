import pytest

from pacific import config
from pacific.config import errors


def test_parse_apps():
    apps_mapping = {
        'reef': {}
    }
    with pytest.raises(errors.ImproperlyConfigured):
        config.parse_apps(apps_mapping)

    apps_mapping['reef']['url_prefix'] = '/'
    result = config.parse_apps(apps_mapping)
    assert 'reef=>/' in result
