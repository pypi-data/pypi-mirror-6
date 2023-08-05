from cratis.features import Feature


class Content(Feature):

    def configure_settings(self, cls):
        self.append_apps(cls, ['cratis.app.content'])
