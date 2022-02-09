# Run using python3 -m pytest argutils/tests.py

import tskit
import pytest
import numpy as np

import argutils


class TestSimulate:
    def test_basic_coalescent(self):
        ts = argutils.sim_coalescent(4, L=5, rho=0.1, seed=1)
        assert ts.num_samples == 4
        assert ts.sequence_length == 5
        assert ts.num_trees > 1
        assert all(tree.num_roots == 1 for tree in ts.trees())

    def test_basic_wright_fisher(self):
        ts = argutils.sim_wright_fisher(4, N=10, L=5, seed=1)
        assert ts.num_samples == 8
        assert ts.sequence_length == 5
        assert ts.num_trees > 1
        assert all(tree.num_roots == 1 for tree in ts.trees())

    def test_basic_coalescent_unresolved(self):
        ts = argutils.sim_coalescent(4, L=5, rho=0.1, seed=1, resolved=False)
        # Very basic - real test is the resolution process.
        assert ts.num_nodes > 4
        assert ts.num_edges > 4

    @pytest.mark.parametrize("seed", range(1, 10))
    @pytest.mark.parametrize(
        ["n", "L"],
        [
            [2, 2],
            [8, 2],
            [16, 2],
            [2, 10],
            [8, 10],
            [16, 10],
            [100, 4],
            [10, 100],
        ],
    )
    def test_coalescent_resolved_equal(self, n, L, seed):
        rho = 0.1
        ts1 = argutils.sim_coalescent(n, L=L, rho=rho, seed=seed, resolved=False)
        ts2 = argutils.sim_coalescent(n, L=L, rho=rho, seed=seed, resolved=True)
        ts3 = ts1.simplify(keep_unary=True)
        # print(ts1.draw_text())
        # print(ts2.draw_text())
        ts2.tables.assert_equals(ts3.tables, ignore_provenance=True)


def gmrca_example_resolved():
    # 3.00┊  5  ┊  5  ┊
    #     ┊  ┃  ┊ ┏┻┓ ┊
    # 2.00┊  4  ┊ 4 ┃ ┊
    #     ┊ ┏┻┓ ┊ ┃ ┃ ┊
    # 1.00┊ ┃ 2 ┊ ┃ 3 ┊
    #     ┊ ┃ ┃ ┊ ┃ ┃ ┊
    # 0.00┊ 0 1 ┊ 0 1 ┊
    #     0     1     2
    tables = tskit.TableCollection(2)
    tables.nodes.add_row(flags=tskit.NODE_IS_SAMPLE, time=0)
    tables.nodes.add_row(flags=tskit.NODE_IS_SAMPLE, time=0)
    tables.nodes.add_row(time=1)
    tables.nodes.add_row(time=1)
    tables.nodes.add_row(time=2)
    tables.nodes.add_row(time=3)

    tables.edges.add_row(0, 2, 4, 0)
    tables.edges.add_row(0, 2, 5, 4)
    tables.edges.add_row(0, 1, 2, 1)
    tables.edges.add_row(0, 1, 4, 2)
    tables.edges.add_row(1, 2, 3, 1)
    tables.edges.add_row(1, 2, 5, 3)
    tables.sort()
    return tables.tree_sequence()


def gmrca_example_unresolved():
    # 3.00┊     5   ┊
    #     ┊  ┏━━┻━┓ ┊
    # 2.00┊  4    ┃ ┊
    #     ┊ ┏┻┓   ┃ ┊
    # 1.00┊ ┃ 2━┳━3 ┊
    #     ┊ ┃   ┃   ┊
    # 0.00┊ 0   1   ┊
    #
    tables = tskit.TableCollection(2)
    tables.nodes.add_row(flags=tskit.NODE_IS_SAMPLE, time=0)
    tables.nodes.add_row(flags=tskit.NODE_IS_SAMPLE, time=0)
    tables.nodes.add_row(time=1)
    tables.nodes.add_row(time=1)
    tables.nodes.add_row(time=2)
    tables.nodes.add_row(time=3)

    tables.edges.add_row(0, 1, 2, 1)
    tables.edges.add_row(1, 2, 3, 1)
    tables.edges.add_row(0, 2, 4, 0)
    tables.edges.add_row(0, 2, 5, 4)
    tables.edges.add_row(0, 2, 4, 2)
    tables.edges.add_row(0, 2, 5, 3)
    tables.sort()
    return tables.tree_sequence()


class TestResolve:
    @pytest.mark.parametrize(
        ["unresolved", "resolved"],
        [(gmrca_example_unresolved(), gmrca_example_resolved())],
    )
    def test_examples(self, unresolved, resolved):
        resolved2 = unresolved.simplify(keep_unary=True)
        # print()
        # print(resolved.draw_text())
        assert resolved.equals(resolved2, ignore_provenance=True)