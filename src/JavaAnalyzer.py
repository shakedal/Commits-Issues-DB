import javalang
import difflib
import Debug
# from javadiff.methodData import SourceLine

"""
def get_method_code(method_name, code):
    tokens = list(javalang.tokenizer.tokenize("".join(code)))
    parser = javalang.parser.Parser(tokens)
    parsed_data = parser.parse().types
    return method_name
"""


def get_content(source_lines):
    content = ""
    for s_line in source_lines:
        content = content + s_line.line
    return content

def get_lines(source_lines):
    lines = list()
    if source_lines is not None:
        for s_line in source_lines:
            lines.append(s_line.line)
    return lines

def analyze_changes(old_lines, new_lines):
    old_content = get_lines(old_lines)
    new_content = get_lines(new_lines)
    diff = difflib.ndiff(old_content, new_content)
    count_old, count_new = 0, 0
    changes = list()

    for line in diff:
        # if Debug.mode:
        #     print(line)
        if line[0] == '-':
            changes.append(ChangedLine("OLD", count_old, line[1:], True, old_lines[count_old].decls))
            count_old += 1
        elif line[0] == '+':
            changes.append(ChangedLine("NEW", count_new, line[1:], True, new_lines[count_new].decls))
            count_new += 1
        elif line[0] == ' ':
            changes.append(ChangedLine("OLD", count_old, line[1:], False, old_lines[count_old].decls))
            count_old += 1
            changes.append(ChangedLine("NEW", count_new, line[1:], False, new_lines[count_new].decls))
            count_new += 1
        elif line[0] == '?':
            continue
        else:
            print("WRONG!!!")

    return changes


class ChangedLine(object):
    def __init__(self, line_type, line_number, content, is_changed, meaning):
        self.line_type = line_type
        self.line_number = line_number
        self.content = content
        self.is_changed = is_changed
        self.meaning = str(meaning)


if __name__ == '__main__':
    text1 = ["abababa", "aaa"]
    text2 = ["aaa", "bbb"]
    diff1 = difflib.ndiff(text1, text2)
    count = 0
    before = list()
    after = list()
    # lines1 = diff1.read()
    # print(diff1)
    for line1 in diff1:
        # if count > 2:
        print("*" + line1[0] + "*")
        count += 1



