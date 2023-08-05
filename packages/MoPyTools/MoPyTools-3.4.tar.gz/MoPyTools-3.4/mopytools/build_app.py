# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is Sync Server
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Tarek Ziade (tarek@mozilla.com)
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****
import os
import sys

from mopytools.util import (timeout, get_options, step, get_channel,
                            update_cmd, is_meta_project, PYTHON, run, PIP,
                            REPO_ROOT, has_changes, is_git, get_non_pinned,
                            DependencyError)
from mopytools.build import get_environ_info, updating_repo


@timeout(4.0)
def main():
    options, args = get_options()

    if len(args) > 0:
        deps = [dep.strip() for dep in args[0].split(',')]
    else:
        deps = []

    # check the provided values in the environ
    if 'LATEST_TAGS' in os.environ:
        raise ValueError("LATEST_TAGS is deprecated, use channels")

    # get the channel
    channel = get_channel(options)
    print("The current channel is %s." % channel)

    _buildapp(channel, deps, options.force, options.timeout, options.verbose,
              options.index, options.extras, options.download_cache)


@step('Building the app')
def _buildapp(channel, deps, force, timeout, verbose, index, extras, cache):
    # check the environ
    name, specific_tags = get_environ_info(deps)

    # updating the repo
    updating_repo(name, channel, specific_tags, force, timeout, verbose)

    # building internal deps first
    build_deps(deps, channel, specific_tags, timeout, verbose)

    # building the external deps now
    build_external_deps(channel, index, extras, timeout, verbose, cache)

    # if the current repo is a meta-repo, running tip on it
    if is_meta_project():
        specific_tags = False
        channel = "dev"

    # build the app now
    build_core_app(timeout, verbose)


@step('Now building the app itself')
def build_core_app(timeout=300, verbose=False):
    run('%s setup.py develop' % PYTHON, timeout, verbose)


def _is_git_repo(url):
    # lame but enough for now
    return url.startswith('git://') or 'github.com' in url


_REPO_SCHEMES = ('git', 'https', 'ssh')


@step("Getting %(dep)s")
def build_dep(dep=None, deps_dir=None, channel='prod', specific_tags=False,
              timeout=300, verbose=False):

    # using REPO_ROOT if the provided dep is not an URL
    is_url = False
    for scheme in _REPO_SCHEMES:
        if dep.startswith(scheme):
            is_url = True
            break

    if not is_url:
        repo = REPO_ROOT + dep
    else:
        repo = dep

    target = os.path.join(deps_dir, os.path.basename(dep))
    if os.path.exists(target):
        os.chdir(target)
        if is_git():
            run('git fetch')
        else:
            run('hg pull')
    else:
        # let's try to detect the repo kind with a few heuristics
        if _is_git_repo(repo):
            run('git clone %s %s' % (repo, target))
        else:
            run('hg clone %s %s' % (repo, target))

        os.chdir(target)

    if has_changes(timeout, verbose):
        if channel != 'dev':
            print('The code was changed, aborting !')
            print('Use the dev channel if you change locally the code')
            sys.exit(0)
        else:
            print('Warning: the code was changed.')

    cmd = update_cmd(dep, channel, specific_tags)
    run(cmd, timeout, verbose)
    run('%s setup.py develop' % PYTHON, timeout, verbose)


@step('Building Services dependencies')
def build_deps(deps, channel, specific_tags, timeout=300, verbose=False):
    """Will make sure dependencies are up-to-date"""
    location = os.getcwd()
    # do we want the latest tags ?
    try:
        deps_dir = os.path.abspath(os.path.join(location, 'deps'))
        if not os.path.exists(deps_dir):
            os.mkdir(deps_dir)

        for dep in deps:
            build_dep(dep=dep, deps_dir=deps_dir, channel=channel,
                      specific_tags=specific_tags, timeout=timeout,
                      verbose=verbose)
    finally:
        os.chdir(location)


@step('Building External dependencies')
def build_external_deps(channel, index, extras, timeout=300, verbose=False,
                        cache=None):
    # looking for a req file
    reqname = '%s-reqs.txt' % channel
    if not os.path.exists(reqname):
        return

    # if not dev, check for pinned versions.
    if channel != 'dev':
        non_pinned = get_non_pinned(reqname)
        if len(non_pinned) > 0:
            deps = ', '.join(non_pinned)
            raise DependencyError('Unpinned dependencies: %s' % deps)

    if os.path.exists('build'):
        root = 'build'
        inc = 1
        while os.path.exists(root + str(inc)):
            inc += 1
        os.rename('build', root + str(inc))

    pip = '%s install -i %s -U -r %s'
    args = (PIP, index, reqname)
    if cache is not None:
        pip += ' --download-cache %s'
        args += (cache,)
    if extras is not None:
        pip += ' --extra-index-url %s'
        args += (extras,)
    run(pip % args, timeout, verbose)
