from pywizard.resources.package_pip import pip_package
from cratis.features import Feature, require


class Filer(Feature):
    """
    Pillow installation

    sudo apt-get install python-dev libjpeg-dev libfreetype6-dev zlib1g-dev

    $ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
    $ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
    $ sudo ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/
    """

    def get_required_packages(self, cls):
        return (
            'easy-thumbnails',
            'Pillow',
            'django-filer'
        )


    def configure_settings(self, cls):

        self.append_apps(cls, [
            'easy_thumbnails',
            'filer',
            'mptt'
        ])

        cls.THUMBNAIL_PROCESSORS = (
            'easy_thumbnails.processors.colorspace',
            'easy_thumbnails.processors.autocrop',
            #'easy_thumbnails.processors.scale_and_crop',
            'filer.thumbnail_processors.scale_and_crop_with_subject_location',
            'easy_thumbnails.processors.filters',
        )

        cls.THUMBNAIL_FORMAT = 'PNG'

        cls.FILER_DEBUG = cls.DEBUG



@require(Filer)
class FilerCms(Feature):

    def get_required_packages(self, cls):
        return 'cmsplugin-filer',


    def configure_settings(self, cls):

        self.append_apps(cls, [
            'cmsplugin_filer_file',
            'cmsplugin_filer_folder',
            'cmsplugin_filer_image',
            'cmsplugin_filer_teaser',
            'cmsplugin_filer_video',
        ])