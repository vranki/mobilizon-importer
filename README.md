# mobilizon-importer

Import events from various data sources to Mobilizon

## Concept

You can write minimal import modules with python. They can read any data source and output Mobilizon event data.
The tool then compares existing events and add new ones to Mobilizon and updates any changes. 

## Modules

 * demopartynet: Import demoparty events from demoparty.net RSS feed. 
 
Write your own, PR's welcome!

## Code

mobilizon.py contains low- and high-level functions to operate on Mobilizon API. It is also a command line tool
that can be used to do various admin things.

mobilizon_importer.py is the main program for importing data. It reads config.json and does the needful.

modules/importmodule.py contains the common code for all import modules. You must inherit your module from this.

## mobilizon.py tool

Command line parameters: operation, email, password, endpoint, identity

Operation is one of: 
 * none (display info)
 * deleteall (deletes all events for the identity)

Identity is the identity to use for stuff. Set to 0 to use default identity.

## Contact

Come to #Mobilizon:matrix.org and ask for cos.

