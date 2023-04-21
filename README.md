# World of Bits Data

Data for the QAWoB and FlightWoB web interaction benchmarks from the [World of Bits](https://proceedings.mlr.press/v70/shi17a.html) paper (Shi et al., 2017). Please use the following citation:

```
@inproceedings{Shi2017WorldOB,
  title={World of Bits: An Open-Domain Platform for Web-Based Agents},
  author={Tianlin Shi and Andrej Karpathy and Linxi (Jim) Fan and Josefa Z. Hern{\'a}ndez and Percy Liang},
  booktitle={International Conference on Machine Learning},
  year={2017},
  url={https://proceedings.mlr.press/v70/shi17a.html},
}
```

# Using the parsed files

* The cache files in `extracted-cache/` contain cached HTML responses. Each archive contains:
  * `index.tsv`: Each line contains:
    * ID
    * URL
    * HTTP method (e.g., GET, POST)
    * Content type
    * Response length
  * `${ID}.entry`: JSON containing information about the request and response.
  * `${ID}.response`: The response. Note that the file is empty if there is no response (usually for POST requests).
* The rewarder files in `parsed-rewarder/` contain task inputs and outputs, as annotated by the crowdworkers.

# Reproducing the parsed files from scratch

**Requirements:** Python 3 and [`rdbtools`](https://pypi.org/project/rdbtools/).

First, download Redis dump [`dump.rdb`](https://nlp.stanford.edu/projects/miniwob/dump.rdb) to `raw/`.

```sh
# Dump the database keys.
rdb raw/dump.rdb -c justkeys | sort | uniq > db-keys.txt

# Extract the cache and rewarder files.
mkdir parsed-cache parsed-rewarder extracted-cache
grep ^cache db-keys.txt | while read x; do python scripts/parse.py --tnetstring $x raw/dump.rdb parsed-cache/$x.json || break; done
grep ^cache db-keys.txt | while read x; do python scripts/extract-responses.py parsed-cache/$x.json extracted-cache/$x || break; done
grep ^rewarder db-keys.txt | while read x; do python scripts/parse.py $x raw/dump.rdb parsed-rewarder/$x.json || break; done
```
