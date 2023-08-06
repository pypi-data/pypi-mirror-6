from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    config.include('pacific.db')

    apps = get_apps_mapping(config)
    for app_name, url_prefix in apps.items():
        config.include(app_name, url_prefix)

    #config.add_static_view('static', 'static', cache_max_age=3600)

    config.scan()
    # We must also scan applications' packages
    for app_name in apps:
        config.scan(app_name)
    return config.make_wsgi_app()


def get_apps_mapping(config):
    """

    :param config:
    :type config: :class:`pyramid.config.Configurator`
    :return: mapping of app_name => app_url_prefix
    :rtype: dict
    """
    apps_list = config.registry.settings['apps'].split(' ')
    apps = {}
    for app_mapping in apps_list:
        app_name, url_prefix = app_mapping.split('=>', 1)
        apps[app_name] = url_prefix
    return apps
