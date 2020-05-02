try:
    from FileDiff import FileDiff
except ImportError:
    from .FileDiff import FileDiff 


class CommitsDiff(object):
    def __init__(self, commit_a, commit_b):
        self.diffs = list(map(lambda d: FileDiff(d, commit_b.hexsha), commit_a.tree.diff(commit_b.tree, ignore_blank_lines=True, ignore_space_at_eol=True)))