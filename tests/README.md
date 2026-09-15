# Graph-art red tests

Run the complete contract suite from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

The suite describes the initial pure `graph_art` API. During the red phase,
missing implementation is reported as assertion failures. Import failures from
unrelated dependencies are still allowed to surface, since they indicate a
broken test environment.
