# Xiangqi Checker

A simple module for checking the legality of xiangqi moves, derived from https://github.com/shaochuan/Xiangqi. Currently untested and experimental.

## Get it
`pip install xiangcheck`

## Use it

Currently uses a move notation that has no relation to the real game. Translation coming soon.

```python
import xiangcheck

checker = xiangcheck.Checker()

# can move a soldier forward?
checker.check_move((4,6),(4,5))
# True

# move that soldier forward
checker.make_move((4,6),(4,5))

# that old move is no longer valid
checker.check_move((4,6),(4,5))
# False
```
