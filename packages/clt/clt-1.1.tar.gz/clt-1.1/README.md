CLI templater (CLT)
===================

A simple command-line tool for convenient templates processing. For example, you have a config file for some web service and just want to put there a different host:port binding
depending on the target server role. Using the tool, you can simply pass the missing variables using syntax like:
```bash
clt --tpl your_file.conf --out test.out --binding 127.0.0.1:9999
```

Examples
--------

Reads infile.tpl template and rewrites its contents to infile.out,
substituting "$$$test":

```bash
clt --tpl infile.tpl --out file.out --delim '$$$' --test 30
```


Reads infile.tpl template and rewrites its contents to outdir/infile.tpl,
substituting "%var1" and "%var2":

```bash
clt --tpl infile.tpl --out outdir --delim '%' --var1 20 --var2 hello
```


Reads all files from indir and rewrites them to outdir,
substituting "$$$var1" and "$$$var2" ("$$$" is the default delimiter):

```bash
clt --tpl indir --out outdir --var1 10 --var2 50
```


Reads all files matching "*.tpl" and rewrites them to
outdir, substituting "$$$var1" and "$$$var2":

```bash
clt --tpl indir/\*.tpl --out outdir --var1 10 --var 20
```

Installation
------------
```bash
pip install clt
```

Python versions supported
------------
Tested with 2.6.x and 2.7.x
