from rogoto import RogotoParser
from rogoto import RogotoParserException


def test_invalid_syntax():
    parser = RogotoParser()
    try:
        parser.parse('goblydegoop')
        raise AssertionError('Should have thrown a RogotoParserException')
    except RogotoParserException:
        pass

def test_pendown():
    parser = RogotoParser()
    results = parser.parse('pendown')
    assert ['pendown'] == results

def test_pendown_abbreviated():
    parser = RogotoParser()
    results = parser.parse('pd')
    assert ['pendown'] == results

def test_penup():
    parser = RogotoParser()
    results = parser.parse('penup')
    assert ['penup'] == results

def test_penup_abbreviated():
    parser = RogotoParser()
    results = parser.parse('pu')
    assert ['penup'] == results

def test_forward():
    parser = RogotoParser()
    results = parser.parse('forward 10')
    assert ['forward 10'] == results

def test_forward_abbreviated():
    parser = RogotoParser()
    results = parser.parse('fd 10')
    assert ['forward 10'] == results

def test_backward():
    parser = RogotoParser()
    results = parser.parse('backward 10')
    assert ['backward 10'] == results

def test_backward_abbreviated():
    parser = RogotoParser()
    results = parser.parse('bk 10')
    assert ['backward 10'] == results

def test_left():
    parser = RogotoParser()
    results = parser.parse('left 10')
    assert ['left 10'] == results

def test_left_abbreviated():
    parser = RogotoParser()
    results = parser.parse('lt 10')
    assert ['left 10'] == results

def test_right():
    parser = RogotoParser()
    results = parser.parse('right 10')
    assert ['right 10'] == results

def test_right_abbreviated():
    parser = RogotoParser()
    results = parser.parse('rt 10')
    assert ['right 10'] == results

def test_can_clear_code_array():
    parser = RogotoParser()
    results = parser.parse('rt 10')
    assert ['right 10'] == results
    parser.clear()
    assert [] == parser.code_to_execute

def test_can_keep_pen_state():
    parser = RogotoParser()
    assert parser.pen_state == 'up'
    parser.parse('pd')
    assert parser.pen_state == 'down'
    parser.parse('penup')
    assert parser.pen_state == 'up'

def test_multiline_parser():
    parser = RogotoParser()
    results = parser.parse('pendown\nfd 10\nlt 45\nfd 10\npenup')
    assert ['pendown', 'forward 10', 'left 45', 'forward 10', 'penup'] == results
