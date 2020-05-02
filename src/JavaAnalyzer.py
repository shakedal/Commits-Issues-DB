import javalang


def get_method_code(method_name, code):
    tokens = list(javalang.tokenizer.tokenize("".join(code)))
    parser = javalang.parser.Parser(tokens)
    parsed_data = parser.parse().types
    return method_name


def get_content(source_lines):
    content = ""
    for s_line in source_lines:
        # TODO: clean tabs
        content = content + s_line.line
    return content
