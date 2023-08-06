import pytest
from .examples import (
    commutativeints, floats, nonuniquelists, unbalancedtrees, exiter
)


@pytest.mark.parametrize(("example", "fork"), [
    (ex, fork)
    for ex in [floats, nonuniquelists, unbalancedtrees]
    for fork in (False, True)
] + [(exiter, True)])
def test_all_examples(example, fork):
    machine = example.machine
    machine.prog_length = 100
    machine.good_enough = 5
    machine.fork = fork
    results = machine.run()
    assert results is not None
    assert len(results) > 0


def test_ints_are_commutative():
    assert commutativeints.machine.run() is None
