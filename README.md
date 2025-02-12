# mobilizon-importer

Import events from various data sources to Mobilizon

## Concept

You can write minimal import modules with python. They can read any data source and output Mobilizon event data.
The tool then compares existing events and add new ones to Mobilizon and updates any changes.

## Modules

* demopartynet: Import demoparty events from demoparty.net RSS feed.
* tampere_events: Import events from city of Tampere.
* ical: Standard ical format calendar

Write your own, PR's welcome!

## Running

Better use pipenv.

```bash
pipenv install
pipenv shell
```


## Configuration

Write a config.json, see config.json.example for example. You can use identity 0 for default identity.

## mobilizon.py tool

### Get account status

```bash
./mobilizon_tool.py status
```

You'll see identity numbers for your groups. You can use these numbers to do operations as.

### List events

```bash
./mobilizon_tool.py list [identity]
```

### Delete ALL events

```bash
./mobilizon_tool.py deleteall [identity]
```

### Delete past events

```bash
./mobilizon_tool.py deletepast [identity]
```

## mobilizon-importer.py

Will run modules and try to import and update any new events to mobilizon.

## Code

mobilizon.py contains low- and high-level functions to operate on Mobilizon API. It is also a command line tool
that can be used to do various admin things.

mobilizon_importer.py is the main program for importing data. It reads config.json and does the needful.

modules/importmodule.py contains the common code for all import modules. You must inherit your module from this.

## Contact

Come to #Mobilizon:matrix.org and ask for cos.
