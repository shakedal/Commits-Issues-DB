import sqlite3
import GitCommits as g
import JiraIssues as j
import JavaAnalyzer as a


def get_connection(path):
    return sqlite3.connect(path)

def close_connection(conn):
    if conn: conn.close()

def insert_project(conn, projectName, JiraProjectId, GitRepositoryPath):
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO Projects (ProjectName, JiraProjectId, GitRepositoryPath) VALUES (?,?,?)"
            cur.execute(SQL, (projectName, JiraProjectId, GitRepositoryPath))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

def insert_issue(conn, issue, projectName):
    # TODO: add time
    issue_id = j.get_issue_id(issue)
    issue_type = j.get_issue_type(issue)
    summary = j.get_issue_summary(issue)
    desc = j.get_issue_description(issue)
    status = j.get_issue_status(issue)

    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO JiraIssues (IssueID, IssueType, ProjectName, Summary, Description, Status) VALUES (?,?,?,?,?,?)"
            cur.execute(SQL, (issue_id, issue_type, projectName, summary, desc, status))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])


def insert_commit(conn, commit, projectName):
    commit_id = g.get_commit_id(commit)
    summary = g.get_commit_name(commit)
    message = g.get_commit_message(commit)
    date = g.get_commit_date(commit)
    parent_id = g.get_commit_parent_id(commit)

    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO Commits (CommitID, ProjectName, Summary, Message, Date, ParentID) VALUES (?,?,?,?,?,?)"
            cur.execute(SQL, (commit_id, projectName, summary, message, date, parent_id))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

    files = g.get_code_file(commit)
    for code_file in files[0]:
        insert_file(conn, commit, code_file, "CODE")
    for test_file in files[1]:
        insert_file(conn, commit, test_file, "TEST")

    changes = g.get_commit_changes(commit)
    for diff in changes:
        insert_changes(conn, commit, diff)


def insert_linkage(conn, commit, issue):
    issue_id = j.get_issue_id(issue)
    commit_id = g.get_commit_id(commit)
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitsIssuesLinkage (IssueID, CommitID) VALUES (?,?)"
            cur.execute(SQL, (issue_id, commit_id))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])


def insert_file(conn, commit, file_path, file_type):
    commit_id = g.get_commit_id(commit)
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitFiles (CommitID, Path, FileType) VALUES (?,?,?)"
            cur.execute(SQL, (commit_id, file_path, file_type))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

def insert_changes(conn, commit, diff):
    commit_id = g.get_commit_id(commit)
    method_name = diff[0]
    new_path = diff[1]
    old_path = diff[3]

    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitChanges (CommitID, MethodName, NewPath, OldPath) VALUES (?,?,?,?)"
            cur.execute(SQL, (commit_id, method_name, new_path, old_path))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

    new_lines = diff[2]
    old_lines = diff[4]
    changed_lines = a.analyze_changes(old_lines, new_lines)

    for line in changed_lines:
        insert_line(conn, commit, method_name, line)

def insert_line(conn, commit, method_name, line):
    commit_id = g.get_commit_id(commit)
    line_type = line.line_type
    line_number = line.line_number
    content = line.content
    changed = line.is_changed
    meaning = line.meaning

    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO MethodData (CommitID, MethodName, OldNew, LineNumber, Content, Changed, Meaning) VALUES (?,?,?,?,?,?,?)"
            cur.execute(SQL, (commit_id, method_name, line_type, line_number, content, changed, meaning))

    except sqlite3.Error as e:
        # print("Error %s:" % e.args[0])
        e = None


if __name__ == '__main__':
    try:
        db_path = r"C:\Users\salmo\Desktop\DnD - Matrix\db\CommitIssueDB.db"
        # issue1 = j.get_issues_list("key = 'LANG-1534'")[0]
        con = get_connection(db_path)
        # insert_project(con, "TEST_project", "T_jiraId", "T_repositoryPath")
        # insert_issue(con, issue1, "TEST_project")
        commit1 = g.get_commit_by_id("63802bf3d5423a8abdc098549b472622a7a43772")
        insert_commit(con, commit1, "TEST_project")
        close_connection(con)
    except ValueError:
        print("Commit not found")
