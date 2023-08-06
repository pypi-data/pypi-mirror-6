# encoding: utf-8

from distutils.core import setup

setup(
    name             = 'cmsplugin_soundcloud',
    version          = '1.0',
    description      = 'Simple Django CMS plugin for embeding sounds from SoundCloud in Your pages',
    long_description = 'Simple Django CMS plugin for embeding sounds from SoundCloud in Your pages',
    author           = 'Jakub Dorňák',
    author_email     = 'jdornak@redhat.com',
    license          = 'BSD',
    url              = 'https://github.com/misli/cmsplugin-soundcloud',
    packages         = ['cmsplugin_soundcloud'],
    package_data     = {'cmsplugin_soundcloud': ['templates/*']},
)
