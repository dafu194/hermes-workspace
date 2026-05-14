from hermes_workspace.core import add, fibonacci


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_fibonacci():
    assert fibonacci(0) == []
    assert fibonacci(1) == [0]
    assert fibonacci(5) == [0, 1, 1, 2, 3]
    assert fibonacci(10)[-1] == 34
