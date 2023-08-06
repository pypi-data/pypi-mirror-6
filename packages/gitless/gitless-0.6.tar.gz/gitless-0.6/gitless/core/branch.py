# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's branching lib."""


import collections
import os
import re

from gitpylib import branch as git_branch
from gitpylib import common as git_common
from gitpylib import file as git_file
from gitpylib import stash as git_stash
from gitpylib import status as git_status

from . import remote as remote_lib
from . import repo as repo_lib


BranchStatus = collections.namedtuple(
    'BranchStatus', ['name', 'is_current', 'upstream', 'upstream_exists'])

# Ret codes of methods.
SUCCESS = 1
REMOTE_NOT_FOUND = 2
INVALID_NAME = 3
BRANCH_ALREADY_EXISTS = 4
NONEXISTENT_BRANCH = 5
BRANCH_IS_CURRENT = 6
INVALID_DP = 7
UPSTREAM_NOT_SET = 8


def create(name, dp='HEAD'):
  """Creates a new branch with the given name.

  Args:
    name: the name of the branch to create.
    dp: divergent point. The commit from where to 'branch out.' (Defaults to
      HEAD.)

  Returns:
    INVALID_NAME, BRANCH_ALREADY_EXISTS, SUCCESS.
  """
  if not name.strip() or '/' in name or '_' in name:
    # Branches can't have a '/' so that we don't confuse them with remote
    # branches that can be specified in the form remote/branch.
    # Also, they can't have a '_' so that it doesn't conflict with our way of
    # naming internal files.
    return INVALID_NAME
  ret = git_branch.create(name, sp=dp)
  if ret == git_branch.INVALID_NAME:
    return INVALID_NAME
  elif ret == git_branch.BRANCH_ALREADY_EXISTS:
    return BRANCH_ALREADY_EXISTS
  elif ret == git_branch.SUCCESS:
    return SUCCESS
  elif ret == git_branch.INVALID_SP:
    return INVALID_DP
  else:
    raise Exception('Unrecognized ret code {0}'.format(ret))


def delete(name):
  """Deletes the branch with the given name.

  Args:
    name: the name of the branch to delete.

  Returns:
    NONEXISTENT_BRANCH or SUCCESS.
  """
  ret = git_branch.force_delete(name)
  if ret == git_branch.NONEXISTENT_BRANCH:
    return NONEXISTENT_BRANCH
  elif ret == SUCCESS:
    # We also cleanup any stash left.
    git_stash.drop(_stash_msg(name))
    return SUCCESS
  else:
    raise Exception('Unrecognized ret code {0}'.format(ret))


def set_upstream(upstream):
  """Sets the upstream branch of the current branch.

  Args:
    upstream: the upstream branch in the form remote/branch.

  Returns:
    REMOTE_NOT_FOUND or SUCCESS.
  """
  upstream_remote, upstream_branch = upstream.split('/')
  if not remote_lib.is_set(upstream_remote):
    return REMOTE_NOT_FOUND

  current_b = current()
  ret = git_branch.set_upstream(current_b, upstream)
  uf = _upstream_file(current_b, upstream_remote, upstream_branch)
  if os.path.exists(uf):
    os.remove(uf)
  if ret == git_branch.UNFETCHED_OBJECT:
    # We work around this, it could be the case that the user is trying to push
    # a new branch to the remote or it could be that the branch exists but it
    # hasn't been fetched yet.
    # TODO(sperezde): fix the fetch case.
    open(uf, 'a').close()
  return SUCCESS


def unset_upstream():
  """Unsets the upstream branch of the current branch."""
  current_b_name = current()
  current_b = status(current_b_name)
  ret = UPSTREAM_NOT_SET
  if current_b.upstream:
    ret = SUCCESS
    if current_b.upstream_exists:
      git_branch.unset_upstream(current_b_name)
    else:
      uf = _upstream_file(current_b_name, *current_b.upstream.split('/'))
      os.remove(uf)
  return ret


def switch(name):
  """Switches to the branch with the given name.

  Args:
    name: the name of the destination branch.

  Returns:
    BRANCH_IS_CURRENT or SUCCESS.
  """
  gl_dir = repo_lib.gl_dir()
  current_b = _current(gl_dir=gl_dir)
  if name == current_b:
    return BRANCH_IS_CURRENT
  # Stash doesn't save assumed unchanged files, so we save which files are
  # marked as assumed unchanged and unmark them. And when switching back we
  # look at this info and re-mark them.
  _unmark_au_files(current_b)
  git_stash.all(_stash_msg(current_b))
  git_branch.checkout(name)
  git_stash.pop(_stash_msg(name))
  _remark_au_files(name, gl_dir=gl_dir)
  return SUCCESS


def current():
  """Get the name of the current branch."""
  return _current()


def status(name):
  """Get the status of the branch with the given name.

  Args:
    name: the name of the branch to status.

  Returns:
    a named tuple (exists, is_current, upstream, upstream_exists) where exists,
    is_current and upstream_exists are boolean values and upstream is a string
    representing its upstream branch (in the form 'remote_name/remote_branch')
    or None if it has no upstream set.
  """
  exists, is_current, upstream = git_branch.status(name)
  if not exists:
    return None
  upstream_exists = True
  if not upstream:
    # We have to check if the branch has an unpushed upstream.
    upstream = _unpushed_upstream(name)
    upstream_exists = False

  return BranchStatus(name, is_current, upstream, upstream_exists)


def status_all():
  """Get the status of all existing branches.

  Returns:
    named tuples of the form (name, is_current, upstream, upstream_exists).
    upstream is in the format 'remote_name/remote_branch'.
  """
  rebase_in_progress = _rebase_in_progress()
  if rebase_in_progress:
    current_b = _rebase_branch()

  ret = []
  for name, is_current, upstream in git_branch.status_all():
    if name == '(no branch)':
      continue

    if rebase_in_progress and name == current_b:
      is_current = current_b

    upstream_exists = True
    if not upstream:
      # We check if the branch has an unpushed upstream
      upstream = _unpushed_upstream(name)
      upstream_exists = False

    ret.append(BranchStatus(name, is_current, upstream, upstream_exists))

  return ret


# Private methods.


def _current(gl_dir=None):
  """Get the name of the current branch.

  Args:
    gl_dir: the gl dir (optional arg for speeding up things).
  """
  gl_dir = repo_lib.gl_dir() if not gl_dir else gl_dir
  if _rebase_in_progress(gl_dir=gl_dir):
    # While in a rebase, Git actually moves to a "no-branch" status.
    # In Gitless, the user is in the branch being re-based.
    return _rebase_branch(gl_dir=gl_dir)
  return git_branch.current()


def _stash_msg(name):
  """Computes the stash msg to use for stashing changes in branch name."""
  return '---gl-{0}---'.format(name)


def _unpushed_upstream(name):
  """Returns the unpushed upstream or None."""
  for f in os.listdir(repo_lib.gl_dir()):
    result = re.match(r'GL_UPSTREAM_{0}_(\w+)_(\w+)'.format(name), f)
    if result:
      return '/'.join([result.group(1), result.group(2)])
  return None


def _upstream_file(branch, upstream_remote, upstream_branch):
  upstream_fn = 'GL_UPSTREAM_{0}_{1}_{2}'.format(
      branch, upstream_remote, upstream_branch)
  return os.path.join(repo_lib.gl_dir(), upstream_fn)


def _unmark_au_files(branch):
  """Saves the path of files marked as assumed unchanged and unmarks them.

  To re-mark all files again use _remark_au_files(branch).

  Args:
    branch: the info will be stored under this branch name.
  """
  assumed_unchanged_fps = git_status.au_files()
  if not assumed_unchanged_fps:
    return

  gl_dir = repo_lib.gl_dir()
  repo_dir = git_common.repo_dir()
  with open(os.path.join(gl_dir, 'GL_AU_{0}'.format(branch)), 'w') as f:
    for fp in assumed_unchanged_fps:
      f.write(fp + '\n')
      git_file.not_assume_unchanged(os.path.join(repo_dir, fp))


def _remark_au_files(branch, gl_dir=None):
  """Re-marks files as assumed unchanged.

  Args:
    branch: the branch name under which the info is stored.
    gl_dir: the gl dir (optional arg for speeding up things).
  """
  gl_dir = repo_lib.gl_dir() if not gl_dir else gl_dir
  au_info_fp = os.path.join(gl_dir, 'GL_AU_{0}'.format(branch))
  if not os.path.exists(au_info_fp):
    return

  repo_dir = git_common.repo_dir()
  with open(au_info_fp, 'r') as f:
    for fp in f:
      fp = fp.strip()
      git_file.assume_unchanged(os.path.join(repo_dir, fp))

  os.remove(au_info_fp)


# Temporal hack until we refactor the sync module.
def _rebase_in_progress(gl_dir=None):
  return os.path.exists(_rebase_file(gl_dir=gl_dir))


def _rebase_branch(gl_dir=None):
  """Gets the name of the current branch being rebased."""
  rf = open(_rebase_file(gl_dir=gl_dir), 'r')
  return rf.readline().strip()


def _rebase_file(gl_dir=None):
  gl_dir = repo_lib.gl_dir() if not gl_dir else gl_dir
  return os.path.join(gl_dir, 'GL_REBASE')
