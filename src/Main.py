import MatrixDB as db
import GitCommits as g
import JiraIssues as j
import Matrix

if __name__ == '__main__':
    # Set variables according to the project
    DB_PATH = r"C:\Users\salmo\Desktop\DnD - Matrix\db\CommitIssueDB.db"
    PROJECT_NAME = "Common-Lang"
    GIT_REPO_PATH = r"https://github.com/apache/commons-lang"
    GIT_REPO_PATH_LOCAL = r"C:\Users\salmo\fsp"
    JIRA_PATH = r"http://issues.apache.org/jira"
    JIRA_PROJECT_ID = "LANG"

    # Get DB connection
    db_connection = db.get_connection(DB_PATH)

    # Project Handling
    db.insert_project(db_connection, PROJECT_NAME, JIRA_PROJECT_ID, GIT_REPO_PATH)

    # Issues Handling
    j.set_jira(JIRA_PATH)
    jql_features = 'project = {0} AND statusCategory = Done'.format(JIRA_PROJECT_ID)
    jql_bugs_improvements = 'project = {0} AND statusCategory = Done'.format(JIRA_PROJECT_ID)

    issues_features = j.get_issues_list(jql_features)
    for issue in issues_features:
        db.insert_issue(db_connection, issue, PROJECT_NAME)

    issues_bugs_improvements = j.get_issues_list(jql_bugs_improvements)
    for issue in issues_bugs_improvements:
        db.insert_issue(db_connection, issue, PROJECT_NAME)

    # Commits Handling
    g.set_repo_path(GIT_REPO_PATH_LOCAL)
    commits = g.filter_commits(g.get_all_commits())

    for commit in commits:
        db.insert_commit(db_connection, commit, PROJECT_NAME)

    # Matrix Handling
    m1 = Matrix.create_matrix(issues_features, commits)
    for issue, commit in m1:
        db.insert_linkage(db_connection, commit, issue)

    m2 = Matrix.create_matrix(issues_bugs_improvements, commits)
    for issue, commit in m2:
        db.insert_linkage(db_connection, commit, issue)

    # DONE
    db.close_connection(db_connection)
