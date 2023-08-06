from dictstyles.styles import toggle_style


def test_dict_to_curly():
    assert toggle_style("{'a': 2}") == "dict(a=2)"

def test_curly_to_dict():
    assert toggle_style("dict(a=2)") == "{'a': 2}"

def test_complex_dict():
    for dict_form, curly_form in [
            ("{'f': some_function(2), 'g': a.b.c.d}", "dict(f=some_function(2), g=a.b.c.d)"),
            ]:
        assert toggle_style(dict_form) == curly_form
        assert toggle_style(curly_form) == dict_form

def test_errors():
    assert toggle_style("{a.b.c.d: 2}") == "{a.b.c.d: 2}"
