from os.path import join as pathjoin
from os.path import exists as pathexists
from os.path import dirname
from os.path import basename
from os import chmod

# import zc.buildout
from sys import platform

template = """#!%(executable)s
import subprocess
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-a", "--admin-user", dest="admin_user",
                    default="%(admin-user)s")
parser.add_argument("-p", "--profile", dest="profile", default='')
parser.add_argument("-u", "--update", dest="update", action='store_true')
parser.add_argument("-z", "--pack", dest="pack", action='store_true')
parser.add_argument("-i", "--install", dest="install", default='')

options = parser.parse_args()

args = "--admin-user " + options.admin_user

if options.profile != '':
    args += " --profile " + options.profile

if options.update:
    args += " --update"

if options.pack:
    args += " --pack"

if options.install != '':
    args += " --install " + options.install


%(zeo-start)s

zopestatus = False
if "program running" in subprocess.check_output(["%(instance-script)s",
                                                 "status"]):
    cmd = "%(instance-script)s stop"
    subprocess.call(cmd.split())
    zopestatus = True

cmd = "%(instance-script)s run %(script)s " + args
subprocess.call(cmd.split())

if zopestatus:
    cmd = "%(instance-script)s start"
    subprocess.call(cmd.split())

%(zeo-stop)s
"""

zeo_start_template = """
zeostatus = False
if "program running" in subprocess.check_output(["bin/zeoserver", "status"]):
    zeostatus = True

if not zeostatus:
    zeo_start = "%(zeo-script)s start"
    subprocess.call(zeo_start.split())"""

zeo_stop_template = """
if not zeostatus:
    zeo_stop = "%(zeo-script)s stop"
    subprocess.call(zeo_stop.split())"""


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.options['bin-directory'] = \
            self.buildout['buildout']['bin-directory']
        self.options['bin_dir'] = self.options['bin-directory']
        self.options.setdefault('admin-user', 'admin')
        self.options.setdefault('zope_part', 'instance')
        self.options.setdefault('zeo_part', '')
        self.options.setdefault('zeo-start', '')
        self.options.setdefault('zeo-stop', '')

        python = buildout['buildout']['python']
        self.options['executable'] = buildout[python]['executable']

        self.options['script'] = pathjoin(dirname(__file__), 'ploneupdater.py')

        self.find_zeo_part()
        self.find_zope_part()

        self.is_win = platform[:3].lower() == "win"

        self.set_instance_scipt()
        if self.options['zeo_part']:
            self.set_zeo_scipt()

    def find_zeo_part(self):
        zeo_recipes = ('plone.recipe.zeoserver', 'plone.recipe.zope2zeoserver')
        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zeo_recipes:
                self.options['zeo_part'] = id
                break

    def find_zope_part(self):
        zope_recipes = ('plone.recipe.zope2instance')
        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zope_recipes:
                self.options['zope_part'] = id
                break

    def set_instance_scipt(self):
        instance = self.buildout[self.options['zope_part']]
        instance_home = instance['location']
        instance_script = self.options['bin_dir'] + '/' + basename(instance_home)
        if self.is_win:
            instance_script = "%s.exe" % instance_script
        self.options['instance-script'] = instance_script

    def set_zeo_scipt(self):
        if self.is_win:
            if pathexists(pathjoin(self.options['bin-directory'],
                          'zeoservice.exe')):
                zeo_script = 'zeoservice.exe'
            else:
                zeo_script = "%s_service.exe" % self.options['zeo_part']
        else:
            zeo_home = self.buildout[self.options['zeo_part']]['location']
            zeo_script = self.options['bin_dir'] + '/' + basename(zeo_home)
        self.options['zeo-script'] = zeo_script
        self.options['zeo-start'] = zeo_start_template % self.options
        self.options['zeo-stop'] = zeo_stop_template % self.options

    def install(self):
        script_path = pathjoin(self.options['bin-directory'], self.name)
        open(script_path, 'w+').write(template % self.options)

        chmod(script_path, 0700)

        return tuple()

    def update(self):
        self.install()
