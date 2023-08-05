import errno
import glob
import hexagonit.recipe.download
import logging
import os
import re
import shutil
import subprocess
import urllib
import zc.buildout

from string import strip

class Recipe(object):
    """zc.buildout recipe for compiling and installing software"""

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.log = logging.getLogger(name)

        options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
            )

        if 'gems' not in options:
            self.log.error("Missing 'gems' option.")
            raise zc.buildout.UserError('Configuration error')

        self.gems = options['gems'].split()
        self.version = options.get('version')
        self.url = options.get('url')
        # Allow to define specific ruby executable. If not, take just 'ruby'
        self.ruby_executable = options.get('ruby-executable', 'ruby')

    def run(self, cmd, environ=None):
        """Run the given ``cmd`` in a child process."""
        log = logging.getLogger(self.name)

        env = os.environ.copy()
        if environ:
            env.update(environ)

        try:
            retcode = subprocess.call(cmd, shell=True, env=env)

            if retcode < 0:
                log.error('Command received signal %s: %s' % (-retcode, cmd))
                raise zc.buildout.UserError('System error')
            elif retcode > 0:
                log.error('Command failed with exit code %s: %s' % (retcode, cmd))
                raise zc.buildout.UserError('System error')
        except OSError, e:
            log.error('Command failed: %s: %s' % (e, cmd))
            raise zc.buildout.UserError('System error')

    def update(self):
        pass

    def _join_paths(self, *paths):
        return ':'.join(filter(None, paths))

    def _get_env_override(self, env):
        env = filter(None, map(strip, env.splitlines()))
        try:
            env = [map(strip, line.split('=', 1)) for line in env]
        except ValueError: # Unpacking impossible
            self.log.error("Every environment line should contain a '=' sign")
            zc.buildout.UserError('Configuration error')
        return env

    def _get_env(self):
        s = {
            'PATH': os.environ.get('PATH', ''),
            'PREFIX': self.options['location'],
            'RUBYLIB': os.environ.get('RUBYLIB', ''),
        }
        env = {
            'GEM_HOME': '%(PREFIX)s/lib/ruby/gems/1.8' % s,
            'RUBYLIB': self._join_paths(
                    '%(RUBYLIB)s',
                    '%(PREFIX)s/lib',
                    '%(PREFIX)s/lib/ruby',
                    '%(PREFIX)s/lib/site_ruby/1.8',
                ) % s,
            'PATH': self._join_paths(
                    '%(PATH)s',
                    '%(PREFIX)s/bin',
                ) % s,
        }
        env_override = self.options.get('environment', '')
        env_override = self._get_env_override(env_override)
        env.update({k: v % env for k, v in env_override})
        return env

    def _get_latest_rubygems(self):
        if self.url:
            version = self.version
            if not version:
                version = re.search(r'rubygems-([0-9.]+).zip$', self.url).group(1)
            return (self.url, version)

        if self.version:
            return ('http://production.cf.rubygems.org/rubygems/'
                    'rubygems-%s.zip' % self.version, self.version)

        f = urllib.urlopen('http://rubygems.org/pages/download')
        s = f.read()
        s = unicode(s)
        f.close()
        r = re.search(r'http://production.cf.rubygems.org/rubygems/'
                      r'rubygems-([0-9.]+).zip', s)
        if r:
            url = r.group(0)
            version = r.group(1)
            return (url, version)
        else:
            return None

    def _install_rubygems(self):
        url, version = self._get_latest_rubygems()

        opt = self.options.copy()
        opt['url'] = url
        opt['destination'] = self.buildout['buildout']['parts-directory']
        hexagonit.recipe.download.Recipe(self.buildout, self.name,
                                         opt).install()

        current_dir = os.getcwd()
        try:
            os.mkdir(self.options['location'])
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass

        srcdir = os.path.join(self.buildout['buildout']['parts-directory'],
                              'rubygems-%s' % version)
        os.chdir(srcdir)

        try:
            env = self._get_env()
            env['PREFIX'] = self.options['location']

            s = {
                'OPTIONS': ' '.join([
                        '--prefix=%s' % self.options['location'],
                        '--no-rdoc',
                        '--no-ri',
                    ]),
                'RUBY': self.ruby_executable,
            }
            self.run('%(RUBY)s setup.rb all %(OPTIONS)s' % s, env)
        finally:
            shutil.rmtree(srcdir)
            os.chdir(current_dir)

    def _install_executable(self, path):
        content = ['#!/bin/sh']
        for key, val in self._get_env().items():
            content.append("export %s='%s'" % (key, val))
        content.append('%s "$@"' % path)
        name = os.path.basename(path)
        bindir = self.buildout['buildout']['bin-directory']
        executable = os.path.join(bindir, name)
        f = open(executable, 'w')
        f.write('\n'.join(content) + '\n\n')
        f.close()
        os.chmod(executable, 0755)
        return executable

    def get_gem_executable(self, bindir):
        gem_executable = os.path.join(bindir, 'gem')
        gem_executable = glob.glob(gem_executable + '*')

        if gem_executable:
            return gem_executable[0]

    def install(self):
        parts = [self.options['location']]

        bindir = os.path.join(self.options['location'], 'bin')
        gem_executable = self.get_gem_executable(bindir)

        if not gem_executable:
            self._install_rubygems()
            gem_executable = self.get_gem_executable(bindir)

        for gemname in self.gems:
            extra = self.options.get('gem-options', '')
            extra = ' '.join(filter(None, map(strip, extra.splitlines())))
            s = {
                'GEM': gem_executable,
                'OPTIONS': ' '.join([
                        '--no-rdoc',
                        '--no-ri',
                        '--bindir=%s' % bindir,
                    ]),
                'EXTRA': extra,
            }
            if '==' in gemname:
                gemname, version = map(strip, gemname.split('==', 1))
                s['GEMNAME'] = gemname
                s['OPTIONS'] += ' --version %s' % version
            else:
                s['GEMNAME'] = gemname
            self.run('%(GEM)s install %(OPTIONS)s %(GEMNAME)s -- %(EXTRA)s' % s,
                     self._get_env())

        for executable in os.listdir(bindir):
            installed_path = self._install_executable(
                    os.path.join(bindir, executable))
            parts.append(installed_path)

        return parts
