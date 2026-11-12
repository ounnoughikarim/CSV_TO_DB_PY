import pytest


def num_batches(total_rows, batch_size):
    return (total_rows + batch_size - 1) // batch_size


def batch_end_index(start_idx, batch_size, total_rows):
    return min(start_idx + batch_size, total_rows)


@pytest.mark.parametrize(
    "total_rows,batch_size,expected",
    [
        (50, 100000, 1),
        (150000, 100000, 2),
        (250000, 100000, 3),
        (100000, 100000, 1),
    ],
)
def test_number_of_batches(total_rows, batch_size, expected):
    assert num_batches(total_rows, batch_size) == expected


def test_batch_slicing_bounds():
    total_rows, batch_size = 250000, 100000
    batches = [
        (i, batch_end_index(i, batch_size, total_rows))
        for i in range(0, total_rows, batch_size)
    ]
    assert batches == [(0, 100000), (100000, 200000), (200000, 250000)]
    assert batches[0][0] == 0
    assert batches[-1][1] == total_rows
    assert sum(end - start for start, end in batches) == total_rows
