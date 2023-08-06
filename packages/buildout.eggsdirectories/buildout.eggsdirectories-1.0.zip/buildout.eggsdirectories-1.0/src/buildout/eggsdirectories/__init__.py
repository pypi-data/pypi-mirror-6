import os

from zc.buildout.easy_install import buildout_and_setuptools_path


MISSING = 'Eggs-directories: "{}" does not exist.'
INCLUDING = 'Eggs-directories: include "{}".'


def extend(buildout):
    option = buildout['buildout']['eggs-directories']
    directories = option.split()
    include_eggs_directories(buildout, directories)


def include_eggs_directories(buildout, directories):
    for directory in directories:
        if os.path.exists(directory):
            msg = INCLUDING.format(directory)
            buildout._logger.info(msg)
            for file in os.listdir(directory):
                buildout_and_setuptools_path.append(
                    os.path.join(directory, file))
        else:
            msg = MISSING.format(directory)
            buildout._logger.warning(msg)
