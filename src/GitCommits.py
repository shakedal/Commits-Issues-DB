import git
import os
import difflib
from javadiff import diff as d
import Debug
import JavaAnalyzer as a

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = r"C:\Program Files\Git\bin\git.exe"

REPO_PATH = r"C:\Users\salmo\fsp"


def get_all_commits(repo_path):
    repo = git.Repo(repo_path)
    all_commits = []
    if not repo.bare:  # check that the repository loaded correctly
        all_commits = list(repo.iter_commits())
        if Debug.mode():
            print("commit list done")
    return all_commits


def filter_commits(commits_list):  # return a list with commits that has java files
    commits = []
    for commit in commits_list:
        files = get_code_file(commit)
        if (len(files[0]) > 0) | (len(files[1]) > 0):  # contain java files (code or test)
            commits.append(commit)
            print("added")
    return commits


def get_code_file(commit):
    file_paths = commit.stats.files.keys()
    code = list()
    test = list()
    for path in file_paths:
        if path.endswith(".java"):
            if "test" in path.lower():
                test.append(path)
            else:
                code.append(path)       
    return code, test


def get_commit_name(commit):
    return commit.summary


def test_diff(commit):
    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
    diffs = commit.diff(parent)
    relevant_data = []
    for diff_item in diffs.iter_change_type('M'):
        if diff_item.a_path.endswith(".java"):
            # read before and after commit to files
            before_code = diff_item.a_blob.data_stream.read().decode('utf-8')
            with open("before.txt", "w", encoding="utf-8") as f:
                f.write(before_code)
                f.close()
            after_code = diff_item.b_blob.data_stream.read().decode('utf-8')
            with open("after.txt", "w", encoding="utf-8") as f:
                f.write(after_code)
                f.close()

            # create changes file
            text1 = open("before.txt").readlines()
            text2 = open("after.txt").readlines()
            with open("compare.txt", "w", encoding="utf-8") as f:
                f.writelines(difflib.unified_diff(text2, text1))
                f.close()

            # separate diffs to functions
            functions = []
            with open('compare.txt') as fp:
                contents = fp.read()
                funcs = contents.split("public")  # TODO: split also private and protected
                for func in funcs[1:]:
                    func = "".join(["public ", func])
                    functions.append(func)
                f.close()
            relevant_data.append((diff_item.a_path, functions))
    return relevant_data


def get_commit_new_code(commit, repo_path):
    relevant_data = []
    methods_before, methods_after = d.get_changed_methods(repo_path, commit)  # amir's - return all methods relevant to the commit
    before_dict = {m.signature: (m.file_name, a.get_content(m.source_lines)) for m in methods_before}
    for new_method in methods_after:
        to_add = False
        new_path = new_method.file_name
        method_name = new_method.signature
        new_content = a.get_content(new_method.source_lines)

        old_path, old_content = before_dict.get(method_name, (None, None))
        if (old_content is None) | (old_path is None):  # new method
            to_add = True
        else:
            before_dict.pop(method_name)
            if (old_content != new_content) | (old_path != new_path):  # something has changed
                to_add = True
            
        if to_add:
            relevant_data.append((method_name, new_path, new_content, old_path, old_content))

    for method_name, (old_path, old_content) in before_dict.items():
        relevant_data.append((method_name, None, None, old_path, old_content))

    return relevant_data




