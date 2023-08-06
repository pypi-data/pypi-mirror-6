""" Pacific Config utilities
"""
from . import errors


def parse_db_settings(db):
    """
    :param db:
    :type db: dict
    :rtype: dict
    """
    rv = {}
    for cluster in db:
        for db_name, credentials in db[cluster].items():
            item = 'pacific.db.{}.{}'.format(cluster, db_name)
            rv[item] = 'postgresql+psycopg2://{user}:{password}@:{port}/{database}?host={host}'.format(**credentials)
    return rv


def parse_apps(apps):
    """
    :param apps: a mapping of activated applications => URL prefixes
    :type apps: dict
    :return: string in form of "{app_name}=>{url_prefix} ..."
    :rtype: str
    """
    prepared = []
    for app_name, attributes in apps.items():
        try:
            prepared.append('{}=>{}'.format(app_name, attributes['url_prefix']))
        except KeyError:
            raise errors.ImproperlyConfigured(
                "Configuration for the {app} app doesn't contain the url_prefix attribute.".format(app=app_name))
    return ' '.join(prepared)