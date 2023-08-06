# vim: sw=2 sts=2 ts=2 et fdm=marker cms=\ #\ %s
# Copyright (c) Roman Neuhauser
# Distributed under the GPLv3+ license (see LICENSE.gpl file)
"""generate a summary of pending changes
"""

testedwith = '2.4.2 2.7.1 2.9.1'
buglink    = 'https://bitbucket.org/roman.neuhauser/hg-request-pull/issues'

from mercurial import commands
from mercurial import error
from mercurial import hg
from mercurial import util
from mercurial.node import short

# remoterepo leaks this one
import urllib2.URLError

def resolver(repo): # {{{
  def resolve(revspec):
    revs = repo.revs(revspec)
    if 1 == len(revs):
      return repo[revs[0]]
    if 0 == len(revs):
      raise util.Abort('%s specifies no revisions')
    raise util.Abort('%s specifies more than one revision')
  return resolve
  # }}}

class Commands(object):
  def __init__(proxy, delegate, ui, repo):
    proxy.delegate = delegate
    proxy.ui = ui
    proxy.repo = repo
  def diff(proxy, *args, **kwargs):
    proxy.delegate.diff(proxy.ui, proxy.repo, *args, **kwargs)
  def log(proxy, *args, **kwargs):
    proxy.delegate.log(proxy.ui, proxy.repo, *args, **kwargs)

class PullRequest(object): # {{{
  def __init__(pr, ui, repo, commands, url, resolver, base, head, opts): # {{{
    resolve = resolver(repo)

    base = resolve(base)
    head = resolve(head)

    revs = map(str, repo.revs('%s .. %s', base, head))
    if 0 == len(revs):
      raise util.Abort('%s does not descend from %s' % (head, base))

    offered = revs[:]
    if int(base) != -1:
      offered = offered[1:]
    if 0 == len(offered):
      raise util.Abort('requested range (%s, %s] is empty' % (base, head))

    pr.ui       = ui
    pr.repo     = repo
    pr.url      = url
    pr.base     = base
    pr.head     = head
    pr.offered  = offered
    cfg = dict(
      bitbucket = pr._getopt(opts, ui.configbool, 'bitbucket'),
      checks    = pr._getopt(opts, ui.configint,  'checks'),
      patch     = pr._getopt(opts, ui.configbool, 'patch'),
    )
    pr.opts     = cfg
    pr.logtpl   = '  {node|short} {desc|firstline|nonempty}\n'
    pr.commands = commands
    pr._check_consistency(url, head)
  # }}}

  def _getopt(pr, opts, meth, name):
    return meth('request-pull', name, opts.get(name))

  def _check_consistency(pr, url, rev): # {{{
    if pr.opts.get('checks') and pr.is_flawed(url, rev, pr.opts):
      pr.complain(
        'Consistency check failed.',
        '%s is inaccessible or does not contain %s.' % (
          url,
          rev,
        )
      )
  # }}}

  def is_flawed(pr, url, head, opts): # {{{
    source, _ = hg.parseurl(url)
    try:
      peer = hg.peer(pr.ui, opts, source)
      peer.lookup(str(head))
      return False
    except (error.RepoError, urllib2.URLError) as e:
      return True
  # }}}

  def complain(pr, *msgs): # {{{
    if 0 == pr.opts.get('checks'):
      return
    if 1 == pr.opts.get('checks'):
      for msg in msgs:
        pr.ui.warn('%s\n' % msg)
      return
    raise util.Abort(''.join([('%s\n' % m) for m in msgs]))
  # }}}

  def display(pr): # {{{
    write = lambda *msgs: pr.ui.write(*msgs)
    write(
      'The following %d commits are available to pull on top of\n\n' % (
      len(pr.offered),
    ))
    pr.log(rev = [str(pr.base)])
    write('\nwith\n\n  hg pull -r %s %s\n\n' % (pr.head, pr.url))
    if pr.opts.get('bitbucket'):
      write('Overview:\n\n  %s/commits/all?search=%s..%s-%s\n\n' % (
        pr.url.rstrip('/'),
        pr.base,
        pr.head,
        pr.base,
      ))
    write('Summary (newest on top):\n\n')
    pr.log(rev = reversed(pr.offered))
    write('\n')
    pr.diff(stat = True)
    if not pr.opts.get('patch'):
      return
    write('\n')
    pr.diff(pager = False)
  # }}}

  def diff(pr, **opts):
    pr.commands.diff(rev = [str(pr.base), str(pr.head)], git = True, **opts)
  def log(pr, **opts):
    pr.commands.log(template = pr.logtpl, **opts)
# }}}

def request_pull(ui, repo, url, base, head = '.', **opts):
  """Generate a summary of pending changes

  request-pull presents a summary of the commits in the
  (BASE, HEAD] range, including a suitable pull command line,
  and diffstat.

  request-pull can verify that HEAD is available from URL.
  Possible option-arguments for ``-c`` and their behaviors:

  :2: Verify that the requested commits can be pulled
      from URL, abort on error.
  :1: Verify that the requested commits can be pulled
      from URL, complain on error but go on.
  :0: Skip verification.

  ``-c 1`` is assumed unless requested otherwise.

arguments:

  :URL:   Repository to pull from.
  :BASE:  Commit the recipient is assumed to have in their repository.
  :HEAD:  Tip-most commit to include in the pull request.
          Defaults to ``.``.
  """

  PullRequest(
    ui
  , repo
  , Commands(commands, ui, repo)
  , url
  , resolver
  , base
  , head
  , opts
  ).display()

cmdtable = {
  'request-pull': (
    request_pull,
    [
     ('B', 'bitbucket', False, 'Include bitbucket.org-compatible URLs'),
     ('c', 'checks', 1, '''Check consistency with URL'''),
     ('p', 'patch', False, 'Show patch text'),
    ],
    '[-B] [-c LEVEL] [-p] URL BASE [HEAD]'
  )
}
