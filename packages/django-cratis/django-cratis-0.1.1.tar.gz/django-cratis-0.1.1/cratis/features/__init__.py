import re


def require(*requirements):

    def func(object):
        def get_required(self, cls):
            parent_requirements = super(object, self).get_required(cls)

            return tuple(parent_requirements) + tuple(requirements)

        object.get_required = get_required

        return object

    return func


class Feature(object):

    def get_required(self, cls):
        return ()

    def get_required_packages(self, cls):
        return ()

    def configure_settings(self, cls):
        pass

    def configure_urls(self, cls, urls):
        pass

    def append_apps(self, cls, apps):
        for app in apps:
            if app not in cls.INSTALLED_APPS:
                cls.INSTALLED_APPS += (app,)

    def append_middleware(self, cls, classes):
        for classname in classes:
            if classname not in cls.MIDDLEWARE_CLASSES:
                cls.MIDDLEWARE_CLASSES += (classname,)

    def append_template_processor(self, cls, processors):
        for classname in processors:
            if classname not in cls.TEMPLATE_CONTEXT_PROCESSORS:
                cls.TEMPLATE_CONTEXT_PROCESSORS += (classname,)

    def report_failure(self, message_):
        print('%s -> %s' % (type(self), message_))
        exit(1)

    def require_setting(self, cls, pattern):

        pattern = re.compile('^%s$' % pattern)
        for name in dir(self):
            if pattern.match(name):
                if not hasattr(cls, name):
                    print('\n\tFeature %s require setting to be set:\n\n\t- %s\n' % (type(self), name))
                    exit(1)

                schema = getattr(self, name)

                if schema:
                    schema(getattr(cls, name))

                setattr(type(self), name, getattr(cls, name))

