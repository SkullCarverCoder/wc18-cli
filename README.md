 <p align="center">
  <img src=https://i.imgur.com/m5iCrNu.jpg" width="500px" />
</p>

WC18 CLI
=====
[![PyPI version](https://badge.fury.io/py/wc18-cli.svg)](https://badge.fury.io/py/wc18-cli)

An easy command line interface for the 2018 World Cup

![](https://i.imgur.com/ylQ9kM3.gif)

Install
=====

No need to get an API key! , wc18-cli uses a json file from [lsv fifa-worldcup-2018](https://github.com/lsv/fifa-worldcup-2018) that is updated frecuently

### Using `pip`

<p> wc18-cli is only supported with python 3.6 due to the use of f-strings be aware before pip installing </p>

```bash
$ pip install wc18-cli
```

### Build from source

```bash
$ git clone https://github.com/SkullCarverCoder/wc18-cli.git
$ cd wc18-cli
$ python setup.py install
```
Usage
=====

### Get info of an specific Country and it's soonest match

```bash
$ wc18 --country=germany # Japan is the name of the team desired to see stats
```


### Get info of an specific Country plus all the matches

```bash
$ wc18 --country=Argentina --allmatches=True # Japan is the name of the team desired to see stats
```

 <p align="center">
  <img src="https://i.imgur.com/FDLQ13Q.gif" width="700px" />
</p>

### Get info table of a group

```bash
$ wc18 --group=d # groups letter must be in lower case
```

<p align="center">
  <img src="https://i.imgur.com/HqxSKO0.gif" width="700px" />
</p>

### Help

```bash
$ wc18 --help
```

Todo
====
- [x] Add Group statistics
- [ ] Enable cache
- [ ] Add  test cases
- [ ] Add knockoff matches logic
- [ ] Add watch for live score scraping from twitter

<p> Feel free to contact me to my email for ideas and to fork this Repo! </p>

Licence
====
Open sourced under [MIT License](LICENSE)

