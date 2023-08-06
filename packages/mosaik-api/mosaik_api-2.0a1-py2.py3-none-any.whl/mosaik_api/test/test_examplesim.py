import pytest

from example_sim import mosaik
import mosaik_api


@pytest.fixture
def sim():
    sim = mosaik.ExampleSim()
    sim.init(step_size=1)
    return sim


def test_sim(sim):
    assert sim.step_size == 1
    assert sim.simulators == []
    assert sim.meta == {
        'api_version': mosaik_api.__version__,
        'models': {
            'A': {
                'public': True,
                'params': ['init_val'],
                'attrs': ['val_out', 'dummy_out'],
            },
            'B': {
                'public': True,
                'params': ['init_val'],
                'attrs': ['val_in', 'val_out', 'dummy_in'],
            },
            'C': {
                'public': False,
            }
        },
    }


def test_create(sim):
    entities = sim.create(2, 'A', init_val=2)
    assert entities == [
        {'eid': '0.0', 'type': 'A', 'rel': []},
        {'eid': '0.1', 'type': 'A', 'rel': []},
    ]
    assert sim.simulators[0].results == [2, 2]

    entities = sim.create(1, 'B', init_val=3)
    assert entities == [
        {'eid': '1.0', 'type': 'B', 'rel': []},
    ]
    assert sim.simulators[1].results == [3]


def test_step_get_data(sim):
    sim.create(1, 'A', init_val=0)
    sim.create(1, 'B', init_val=0)
    ret = sim.step(0, {'1.0': {'val_in': [1, 2]}})
    assert ret == 1

    data = sim.get_data({'0.0': ['val_out', 'spam'], '1.0': ['val_out']})
    assert data == {'0.0': {'val_out': 1}, '1.0': {'val_out': 3}}

    sim.step_size = 2
    ret = sim.step(1, {'1.0': {'val_in': [5]}})
    assert ret == 3

    data = sim.get_data({'1.0': ['val_out']})
    assert data == {'1.0': {'val_out': 5}}

    ret = sim.step(3, {})
    data = sim.get_data({'1.0': ['val_out']})
    assert data == {'1.0': {'val_out': 5}}
