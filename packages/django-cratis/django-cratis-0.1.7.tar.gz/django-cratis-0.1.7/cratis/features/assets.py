from cratis.features import Feature


class Compressor(Feature):
    def configure_settings(self, cls):
        self.append_apps(cls, ['compressor'])

        cls.STATICFILES_FINDERS = cls.STATICFILES_FINDERS + (
            'compressor.finders.CompressorFinder',
        )