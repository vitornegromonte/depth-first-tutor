# Learning tree: binary search

Goal: how does binary search find an item in O(log n)?
Sources:
- Knuth, The Art of Computer Programming, Vol. 3: Sorting and Searching, 2nd ed. (1998), §6.2.1, Algorithm B · binary search on an ordered table
Started: 2026-10-09
Grammar: depth-first-tutor (references/tree.md)

> Illustrative example written for the README, not the record of a real session.

## Tree

- [CLOSED] (U) why must the array be sorted? → otherwise one comparison says nothing about which half holds the item (2026-10-09)
- [FOCUS] (N) why does each step halve the search space?
    - [OPEN] what is the invariant between lo and hi? — alias: invariant
    - [CLOSED] (black-box) why is log₂ n the number of halvings? → accepted as given: halving n until 1 is left takes about log₂ n steps (2026-10-09)
    - [DEFERRED] (decision) iterative or recursive version? — reason: decide after the first version works
- [OPEN] (practice) implement it and pass the edge-case tests — depends: invariant
