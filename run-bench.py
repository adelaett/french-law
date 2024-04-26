import csv
from subprocess import run, PIPE
from pathlib import Path
import os
from itertools import product
import shutil
import re
import json

import base64
import os
import hashlib  # for stable hash accross runs
import functools
import operator
env_base = dict(os.environ)


# type t =
# [ `Assoc of (string * t) list
# | `Bool of bool
# | `Float of float
# | `Int of int
# | `List of t list
# | `Null
# | `String of string ]

def flatten(d, names):
    if type(d) == list:
        for i in d:
            for row in flatten(i, names):
                yield row
    if type(d) == dict:
        name, names = names[0], names[1:]
        for k, v in d.items():
            for row in flatten(v, names):
                yield row | {name: k}
    if type(d) in [int, float, bool, str]:
        yield {"value": d}


# for row in flatten([{'Aides au logement': [9711.132648245295],
#                      'Allocations familiales': [44611.98724097165]}], ['example']):
#     print(row)


rows = []
for optim, avoid_exceptions in product(["yes", "no"], repeat=2):

    other = {"NODOC": "yes",
             "CATALA_FLAGS": "",
             "CATALA_TRACE": "no",
             "CATALA_OPTIMIZE": optim,
             "CATALA_AVOID_EXCEPTIONS": avoid_exceptions}

    tmp_dir = (Path(
        '.')/'ex'/hashlib.md5(repr(tuple(sorted(other.items()))).encode('utf-8')).hexdigest()).absolute()

    if not (tmp_dir.exists() and tmp_dir.is_dir()):

        run(["make", "clean", "local-install"],
            cwd="../catala-examples",
            capture_output=True,
            check=True, env=env_base | {"INSTALL_PREFIX": tmp_dir} | other
            )

    # Bien garder les deux lignes.

    # interprete catala.
    run(["rm", "_python_venv/french-law.stamp"])
    run(["make", "dependencies-python"], check=True,
        # capture_output=True,
        env=env_base | {"OCAMLPATH": tmp_dir/"lib"})
    result_python = run(["make", "bench_python"], check=True,
                        capture_output=True,
                        env=env_base | {"OCAMLPATH": tmp_dir/"lib"})

    for row in [json.loads(m.group(1)) for m in re.finditer(
        r"#{#([^#]*)#}#",
        result_python.stdout.decode('utf-8'),
        flags=re.MULTILINE
    )]:
        rows.append(row | other | {"lang": "python"})

    # Plutot le throughput.

    # C'est quoi l'argument pour le python ? -> on regarde tous les languages.
    # c'est mieux dans tous les cas donc c'était une bonne chose.

    result_ocaml = run(["make", "bench_ocaml"], check=True,
                       capture_output=True,
                       env=env_base | {"OCAMLPATH": tmp_dir/"lib"})

    for row in functools.reduce(operator.iconcat, [json.loads(m.group(1)) for m in re.finditer(
        r"#{#([^#]*)#}#",
        result_ocaml.stdout.decode('utf-8'),
        flags=re.MULTILINE
    )], []):
        rows.append(row | other | {"lang": "ocaml"})

    # shutil.rmtree(tmp_dir)

with open('benches.csv', 'w', newline='') as csvfile:
    fieldnames = functools.reduce(
        operator.or_, [row.keys() for row in rows], set()
    )

    print(fieldnames)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in rows:
        writer.writerow(row)
