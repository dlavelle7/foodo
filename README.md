FooDo - A Command Line ToDo App
===============================

A command line todo app written in Python using SQLALchemy with a SQLlite database.

Installation
------------
* Clone repo
* pip install -r requirements.txt
* cd foodo/
* python setup.py install

Examples
--------
List your foodos (verbosely!):
```bash
(foodo) david@david-HP-ENVY-Notebook:~/workspace/foodo$ foodo list -v
╒══════╤═══════════════════╤════════════════╤══════════╕
│   Id │ Title             │ Date           │ Status   │
╞══════╪═══════════════════╪════════════════╪══════════╡
│    1 │ update readme     │ 20:59 20-10-16 │ complete │
├──────┼───────────────────┼────────────────┼──────────┤
│    2 │ make the dinner   │ 21:02 20-10-16 │ active   │
├──────┼───────────────────┼────────────────┼──────────┤
│    3 │ feed the cat      │ 21:02 20-10-16 │ complete │
├──────┼───────────────────┼────────────────┼──────────┤
│    4 │ take out the bins │ 21:03 20-10-16 │ active   │
├──────┼───────────────────┼────────────────┼──────────┤
│    5 │ write some code   │ 21:03 20-10-16 │ active   │
├──────┼───────────────────┼────────────────┼──────────┤
│    6 │ go to the gym!    │ 21:04 20-10-16 │ complete │
╘══════╧═══════════════════╧════════════════╧══════════╛
```

List only active foodos:
```bash
(foodo) david@david-HP-ENVY-Notebook:~/workspace/foodo$ foodo list -a
  Id  Title              Date            Status
----  -----------------  --------------  --------
   2  make the dinner    21:02 20-10-16  active
   4  take out the bins  21:03 20-10-16  active
   5  write some code    21:03 20-10-16  active
```

List only selected columns of completed foodos:
```bash
(foodo) david@david-HP-ENVY-Notebook:~/workspace/foodo$ foodo list -col Id Title -c
  Id  Title
----  --------------
   1  update readme
   3  feed the cat
   6  go to the gym!
```

Foodo help:
```bash
(foodo) david@david-HP-ENVY-Notebook:~/workspace/foodo$ foodo -h
usage: foodo [-h] {add,set,delete,list} ...

A command line todo app

positional arguments:
  {add,set,delete,list}
    add                 Add a new FooDo
    set                 Set status of your FooDo
    delete              Delete a FooDo
    list                List your FooDos

optional arguments:
  -h, --help            show this help message and exit
```
