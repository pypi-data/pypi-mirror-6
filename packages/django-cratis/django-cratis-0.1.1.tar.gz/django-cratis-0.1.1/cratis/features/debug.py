from pywizard.resources.package_pip import pip_package
from cratis.features import Feature


class Debug(Feature):

    def get_required_packages(self, cls):
        return 'django-debug-toolbar',

    def configure_settings(self, cls):
        self.append_apps(cls, ['debug_toolbar'])
