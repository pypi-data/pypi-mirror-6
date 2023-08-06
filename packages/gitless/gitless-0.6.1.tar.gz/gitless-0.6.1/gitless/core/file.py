# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""Gitless's file lib."""


import collections
import os

from gitpylib import common as git_common
from gitpylib import file as git_file
from gitpylib import status as git_status

from . import repo as repo_lib
from . import branch as branch_lib


# Ret codes of methods.
SUCCESS = 1
FILE_NOT_FOUND = 2
FILE_ALREADY_TRACKED = 3
FILE_ALREADY_UNTRACKED = 4
FILE_IS_UNTRACKED = 5
FILE_NOT_FOUND_AT_CP = 6
FILE_IN_CONFLICT = 7
FILE_IS_IGNORED = 8
FILE_NOT_IN_CONFLICT = 9
FILE_ALREADY_RESOLVED = 10
FILE_IS_DIR = 11

# Possible Gitless's file types.
TRACKED = 12
UNTRACKED = 13
IGNORED = 14

# Possible diff output lines.
DIFF_INFO = git_file.DIFF_INFO  # line carrying diff info for new hunk.
DIFF_SAME = git_file.DIFF_SAME  # line that git diff includes for context.
DIFF_ADDED = git_file.DIFF_ADDED
DIFF_MINUS = git_file.DIFF_MINUS


def track(fp):
  """Start tracking changes to fp.

  Args:
    fp: the file path of the file to track.

  Returns:
    FILE_NOT_FOUND, FILE_IS_DIR, FILE_ALREADY_TRACKED, FILE_IN_CONFLICT,
    FILE_IS_IGNORED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  gl_st, git_s = _status(fp)
  if not gl_st:
    return FILE_NOT_FOUND
  elif gl_st.type == TRACKED:
    return FILE_ALREADY_TRACKED
  elif gl_st.type == IGNORED:
    return FILE_IS_IGNORED

  # If we reached this point we know that the file to track is a untracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git => add the file.
  #   (ii) an assumed unchanged file => unmark it.
  if git_s == git_status.UNTRACKED:
    # Case (i).
    git_file.stage(fp)
  elif (git_s == git_status.ASSUME_UNCHANGED or
        git_s == git_status.DELETED_ASSUME_UNCHANGED):
    # Case (ii).
    git_file.not_assume_unchanged(fp)
  else:
    raise Exception('File {0} in unkown status {1}'.format(fp, git_s))

  return SUCCESS


def untrack(fp):
  """Stop tracking changes to fp.

  Args:
    fp: the file path of the file to untrack.

  Returns:
    FILE_NOT_FOUND, FILE_IS_DIR, FILE_ALREADY_UNTRACKED, FILE_IN_CONFLICT,
    FILE_IS_IGNORED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  gl_st, git_s = _status(fp)
  if not gl_st:
    return FILE_NOT_FOUND
  elif gl_st.type == IGNORED:
    return FILE_IS_IGNORED
  elif gl_st.type == UNTRACKED:
    return FILE_ALREADY_UNTRACKED

  # If we reached this point we know that the file to untrack is a tracked
  # file. This means that in the Git world, the file could be either:
  #   (i)  a new file for Git that is staged (the user executed gl track on a
  #        uncomitted file) => reset changes;
  #   (ii) the file is a previously committed file => mark it as assumed
  #        unchanged.
  if git_s == git_status.STAGED:
    # Case (i).
    git_file.unstage(fp)
  elif (git_s == git_status.TRACKED_UNMODIFIED or
        git_s == git_status.TRACKED_MODIFIED or
        git_s == git_status.DELETED):
    # Case (ii).
    git_file.assume_unchanged(fp)
  elif git_s == git_status.IN_CONFLICT:
    return FILE_IN_CONFLICT
  else:
    raise Exception('File {0} in unkown status {1}'.format(fp, git_s))

  return SUCCESS


def diff(fp):
  """Compute the diff of the given file with its last committed version.

  Args:
    fp: the file path of the file to diff.

  Returns:
    a pair (result, out) where result is one of FILE_NOT_FOUND,
    FILE_IS_UNTRACKED, FILE_IS_DIR or SUCCESS and out is the output of the diff
    command in a machine-friendly way: it's a tuple of the form
    (list of namedtuples with fields 'line', 'status', 'old_line_number',
     'new_line_number', line number padding, additions, deletions).
  """
  nil_out = (None, None, None, None)
  if os.path.isdir(fp):
    return (FILE_IS_DIR, nil_out)
  gl_st, git_s = _status(fp)
  if not gl_st:
    return (FILE_NOT_FOUND, nil_out)
  elif gl_st.type == UNTRACKED:
    return (FILE_IS_UNTRACKED, nil_out)
  elif gl_st.type == IGNORED:
    return (FILE_IS_IGNORED, nil_out)

  do_staged_diff = False
  if git_s == git_status.STAGED:
    do_staged_diff = True
  elif (git_s == git_status.ADDED_MODIFIED or
        git_s == git_status.MODIFIED_MODIFIED):
    git_file.stage(fp)
    do_staged_diff = True

  # Don't include the `git diff` header.
  return (SUCCESS, git_file.diff(fp, staged=do_staged_diff)[:-1])


def checkout(fp, cp='HEAD'):
  """Checkouts file fp at cp.

  Args:
    fp: the filepath to checkout.
    cp: the commit point at which to checkout the file (defaults to HEAD).

  Returns:
    a pair (status, out) where status is one of FILE_IS_DIR,
    FILE_NOT_FOUND_AT_CP or SUCCESS and out is the content of fp at cp.
  """
  if os.path.isdir(fp):
    return (FILE_IS_DIR, None)
  # "show" expects the full path with respect to the repo root.
  rel_fp = os.path.join(repo_lib.cwd(), fp)[1:]
  ret, out = git_file.show(rel_fp, cp)

  if ret == git_file.FILE_NOT_FOUND_AT_CP:
    return (FILE_NOT_FOUND_AT_CP, None)

  s = git_status.of_file(fp)
  unstaged = False
  if s == git_status.STAGED:
    git_file.unstage(fp)
    unstaged = True

  with open(fp, 'w') as dst:
    dst.write(out)

  if unstaged:
    git_file.stage(fp)

  return (SUCCESS, out)


def status(fp):
  """Gets the status of fp.

  Args:
    fp: the file to status.

  Returns:
    None (if the file wasn't found) or a named tuple (fp, type, exists_in_lr,
    exists_in_wd, modified, in_conflict, resolved) where fp is a file path, type
    is one of TRACKED, UNTRACKED or IGNORED and all the remaining fields are
    booleans. The modified field is True if the working version of the file
    differs from its committed version. (If there's no committed version,
    modified is set to True.)
  """
  return _status(fp)[0]


def status_all(include_tracked_unmodified_fps=True):
  """Gets the status of all files relative to the cwd.

  Args:
    include_tracked_unmodified_fps: if True, files that are tracked but
      unmodified will be also reported. Setting it to False improves performance
      significantly if the repo is big. (Defaults to True.)

  Returns:
    a list of named tuples (fp, type, exists_in_lr, exists_in_wd, modified,
    in_conflict, resolved) where fp is a file path, type is one of TRACKED,
    UNTRACKED or IGNORED and all the remaining fields are booleans. The
    modified field is True if the working version of the file differs from its
    committed version. (If there's no committed version, modified is set to
    True.)
  """
  for (s, fp) in git_status.of_repo(
      include_tracked_unmodified_fps=include_tracked_unmodified_fps):
    f_st = _build_f_st(s, fp)
    if f_st:
      yield f_st


def resolve(fp):
  """Marks the given file in conflict as resolved.

  Args:
    fp: the file to mark as resolved.

  Returns:
    FILE_NOT_FOUND, FILE_NOT_IN_CONFLICT, FILE_ALREADY_RESOLVED or SUCCESS.
  """
  if os.path.isdir(fp):
    return FILE_IS_DIR
  f_st = status(fp)
  if not f_st:
    return FILE_NOT_FOUND
  if f_st.resolved:
    return FILE_ALREADY_RESOLVED
  if not f_st.in_conflict:
    return FILE_NOT_IN_CONFLICT

  # We don't use Git to keep track of resolved files, but just to make it feel
  # like doing a resolve in Gitless is similar to doing a resolve in Git
  # (i.e., add) we stage the file.
  git_file.stage(fp)
  # We add a file in the Gitless directory to be able to tell when a file has
  # been marked as resolved.
  # TODO(sperezde): might be easier to just find a way to tell if the file is
  # in the index.
  open(_resolved_file(fp), 'w').close()
  return SUCCESS


def internal_resolved_cleanup():
  for f in os.listdir(repo_lib.gl_dir()):
    if f.startswith('GL_RESOLVED'):
      os.remove(os.path.join(repo_lib.gl_dir(), f))
      #print 'removed %s' % f


# Private methods.


def _status(fp):
  """Get the status of the given fp.

  Returns:
    a tuple (gl_status, git_status) where gl_status is a FileStatus namedtuple
    representing the status of the file (or None if the file doesn't exist) and
    git_status is one of git's possible status for the file.
  """
  git_s = git_status.of_file(fp)
  if git_s == git_status.FILE_NOT_FOUND:
    return (None, git_s)
  gl_s = _build_f_st(git_s, fp)
  if not gl_s:
    return (None, git_s)
  return (gl_s, git_s)


# This namedtuple is only used in _build_f_st, but putting it as a module var
# instead of inside the function significantly improves performance (makes a
# difference when the repo is big).
FileStatus = collections.namedtuple(
    'FileStatus', [
        'fp', 'type', 'exists_in_lr', 'exists_in_wd', 'modified',
        'in_conflict', 'resolved'])


def _build_f_st(s, fp):
  # TODO(sperezde): refactor this.
  # Temporarily disable pylint's too-many-branches warning.
  # pylint: disable=R0912
  ret = None
  if s == git_status.UNTRACKED:
    ret = FileStatus(fp, UNTRACKED, False, True, True, False, False)
  elif s == git_status.TRACKED_UNMODIFIED:
    ret = FileStatus(fp, TRACKED, True, True, False, False, False)
  elif s == git_status.TRACKED_MODIFIED:
    ret = FileStatus(fp, TRACKED, True, True, True, False, False)
  elif s == git_status.STAGED:
    # A file could have been "gl track"ed and later ignored by adding a matching
    # pattern in a .gitignore file. We consider this kind of file to still be a
    # tracked file. This is consistent with the idea that tracked files can't
    # be ignored.
    # TODO(sperezde): address the following rough edge: the user could untrack
    # a tracked file (one that was not committed before) and if it's matched by
    # a .gitignore file it will be ignored. The same thing won't happen if an
    # already committed file is untracked (due to how Gitless keeps track of
    # these kind of files).

    # Staged files don't exist in the lr for Gitless.
    ret = FileStatus(fp, TRACKED, False, True, True, False, False)
  elif s == git_status.ASSUME_UNCHANGED:
    # TODO(sperezde): detect whether it is modified or not?
    ret = FileStatus(fp, UNTRACKED, True, True, True, False, False)
  elif s == git_status.DELETED:
    ret = FileStatus(fp, TRACKED, True, False, True, False, False)
  elif s == git_status.DELETED_STAGED:
    # This can only happen if the user did a rm of a new file. The file doesn't
    # exist as far as Gitless is concerned.
    git_file.unstage(fp)
    ret = None
  elif s == git_status.DELETED_ASSUME_UNCHANGED:
    ret = None
  elif s == git_status.IN_CONFLICT:
    wr = _was_resolved(fp)
    ret = FileStatus(fp, TRACKED, True, True, True, not wr, wr)
  elif s == git_status.IGNORED:
    ret = FileStatus(fp, IGNORED, False, True, True, True, False)
  elif s == git_status.MODIFIED_MODIFIED:
    # The file was marked as resolved and then modified. To Gitless, this is
    # just a regular tracked file.
    ret = FileStatus(fp, TRACKED, True, True, True, False, True)
  elif s == git_status.ADDED_MODIFIED:
    # The file is a new file that was added and then modified. This can only
    # happen if the user gl tracks a file and then modifies it.
    ret = FileStatus(fp, TRACKED, False, True, True, False, False)
  else:
    raise Exception('Unrecognized status {0}'.format(s))
  return ret


def _was_resolved(fp):
  """Returns True if the given file had conflicts and was marked as resolved."""
  return os.path.exists(_resolved_file(fp))


def _resolved_file(fp):
  fp = os.path.relpath(os.path.abspath(fp), git_common.repo_dir())
  fp = fp.replace(os.path.sep, '-')  # this hack will do the trick for now.
  return os.path.join(
      repo_lib.gl_dir(), 'GL_RESOLVED_{0}_{1}'.format(branch_lib.current(), fp))
