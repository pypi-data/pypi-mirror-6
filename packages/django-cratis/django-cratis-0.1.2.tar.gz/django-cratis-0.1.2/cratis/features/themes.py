import os
import pkg_resources
from cratis.features import Feature


class Theme(Feature):
    def __init__(self, name):
        super(Theme, self).__init__()

        self.theme_name = name

    def load_theme(self, cls):

        from cratis.utils.themes import load_theme
        themes_dir = cls.BASE_DIR + os.sep + 'themes'

        themes = {}
        for entry_point in pkg_resources.iter_entry_points('cratis.themes'):
            themes[entry_point.name] = entry_point.load()()  # laod and execute right a way

        theme_config = load_theme({'dir': themes_dir, 'themes': themes}, self.theme_name)


        return theme_config



    def configure_settings(self, cls):
        super(Theme, self).configure_settings(cls)

        from cratis.utils.themes import ThemeLoadException

        try:
            theme_config = self.load_theme(cls)
            cls.THEME_NAME = self.theme_name
            cls.CMS_TEMPLATES += tuple([(path, name) for name, path in theme_config['cms_templates'].items()])

            cls.STATICFILES_DIRS += tuple(theme_config['asset_dirs'])
            cls.TEMPLATE_DIRS += tuple(theme_config['template_dirs'])

        except ThemeLoadException as e:
            self.report_failure('Failed to load theme: %s. Reason: %s' % (self.theme_name, e.message))


class TwitterBootstrap(Feature):

    def configure_settings(self, cls):
        self.append_apps(cls, ('bootstrapform',))