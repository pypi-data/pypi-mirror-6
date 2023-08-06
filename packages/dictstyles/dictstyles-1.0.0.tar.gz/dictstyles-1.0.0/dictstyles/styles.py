import ast

from .utils import unparse


def toggle_style(s):
    if s.startswith("{"):
        return curly_to_dict(s)
    return dict_to_curly(s)

def curly_to_dict(s):
    expr = _get_expr(s)
    returned = ast.Call()
    returned.func = ast.Name()
    returned.func.id = 'dict'
    returned.args = []
    returned.keywords = []
    for key, value in zip(expr.keys, expr.values):
        if not isinstance(key, ast.Str):
            return s
        keyword = ast.keyword(arg=key.s, value=value)
        returned.keywords.append(keyword)
    returned.starargs = None
    returned.kwargs = None
    return unparse(returned)

def dict_to_curly(s):
    expr = _get_expr(s)
    returned = ast.Dict()
    returned.keys = []
    returned.values = []
    for keyword in expr.keywords:
        returned.keys.append(ast.Str(s=keyword.arg))
        returned.values.append(keyword.value)
    return unparse(returned)

def _get_expr(s):
    tree = ast.parse(s)
    [expr] = tree.body
    return expr.value
