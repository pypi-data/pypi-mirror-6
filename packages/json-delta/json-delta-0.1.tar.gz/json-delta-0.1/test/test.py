from __future__ import print_function, unicode_literals

import json
import sys, os

HERE = os.path.abspath(os.path.dirname(__file__))
DOTDOT = os.path.abspath(os.path.join(HERE, '..'))

sys.path.insert(0, os.path.join(DOTDOT, 'src'))
import json_delta
print(json_delta.__file__)

def gather_material(dr=os.path.join(HERE, 'Material')):
    files = set(os.listdir(dr))
    i = 0
    while True:
        out = i
        if not files: 
            break
        for frame in ('case_%02d.json', 'target_%02d.json', 
                      'diff_%02d.json', 'udiff_%02d.patch'):
            if frame % i not in files:
                out = None
            files.discard(frame % i)
        if out is not None:
            yield out
        i += 1

INDICES = [x for x in gather_material()]

def run_diff_case(idx):
    with open(os.path.join(HERE, 'Material', 'case_%02d.json' % idx)) as f:
        case = json.load(f)
    with open(os.path.join(HERE, 'Material', 'target_%02d.json' % idx)) as f:
        target = json.load(f)
    diff = json_delta.diff(case, target, verbose=False)
    assert target == json_delta.patch(case, diff)

def run_patch_case(idx):
    with open(os.path.join(HERE, 'Material', 'case_%02d.json' % idx)) as f:
        case = json.load(f)
    with open(os.path.join(HERE, 'Material', 'target_%02d.json' % idx)) as f:
        target = json.load(f)
    with open(os.path.join(HERE, 'Material', 'diff_%02d.json' % idx)) as f:
        diff = json.load(f)
    assert target == json_delta.patch(case, diff)

def run_udiff_case(idx):
    with open(os.path.join(HERE, 'Material', 'case_%02d.json' % idx)) as f:
        case = json.load(f)
    with open(os.path.join(HERE, 'Material', 'target_%02d.json' % idx)) as f:
        target = json.load(f)
    udiff = '\n'.join(json_delta.udiff(case, target))
    assert target == json_delta.upatch(case, udiff)

def run_upatch_case(idx):
    with open(os.path.join(HERE, 'Material', 'case_%02d.json' % idx)) as f:
        case = json.load(f)
    with open(os.path.join(HERE, 'Material', 'target_%02d.json' % idx)) as f:
        target = json.load(f)
    with open(os.path.join(HERE, 'Material', 'udiff_%02d.patch' % idx)) as f:
        udiff = f.read()
    assert target == json_delta.upatch(case, udiff)

def test_patch():
    for i in INDICES:
        yield run_diff_case, i

def test_upatch():
    for i in INDICES:
        yield run_upatch_case, i

def test_diff():
    for i in INDICES:
        yield run_diff_case, i

def test_udiff():
    for i in INDICES:
        yield run_udiff_case, i

