PricesPaidAPI
=============

Backend and web service for searching a database imported from CSV files (someday generally, but Prices Paid for now.)

This is part of the PricesPaid (P3) Project
--------------------------------------

The PricesPaid (P3) project is market research tool to allow search of purchase transactions.  It is modularized into 4 github repositories:

1. [PricesPaidGUI](https://github.com/XGov/PricesPaidGUI), 
2. [PricesPaidAPI](https://github.com/presidential-innovation-fellows), 
3. [MorrisDataDecorator](https://github.com/presidential-innovation-fellows/MorrisDataDecorator), 
4. [P3Auth](https://github.com/XGov/P3Auth).  

To learn how to install the system, please refer to the documentation in the PricesPaidGUI project.

The name "PricesPaid" is descriptive: this project shows you prices that have been paid for things.  However, the name is applied to many projects, so "P3" is the specific name of this project.


# INTRODUCTION

This is a project written by Robert L. Read, Martin Ringlein, Aaron Snow, and Gregory Godbout, who are all 
Presidential Innovation Fellows (Round 2).  The purpose is to save the Federal Government money by
providing a research tool that shows prices actually paid for commodities and perhaps services.  This is
completely analogous to market research that any buyer would do, although of course other avenues of 
market research should be used as well.

## STATUS

Robert L. Read is the main engineer on this project, which was begun as Presidentional Innovation Fellowship
project in July of 2013. At the time of this writing it is probably not documented well enough to use easily, though
of course I will respond <read.robert@gmail.com> to any questions.

The code is currently in use within the Federal government in a Beta mode, with a plan to roll out to many
federal procurement officers by the summer of 2014.  That website, however, will have data that the government
considers sensitive, and will be available only to federal employees.

However, this code is in the public domain within the United States.  I would love to see it used by someobody else---
for example, a city or state, that wanted to present a simple research tool for price transactions, or to provide their
citizens transparency into their purchases.


## WHY YOU MIGHT CARE

You might find some value in this code if you want an example of using Python code to load a SOLR index.

You might find some value if you want to see an approach to adapting mulitple file formats to loading into 
a single harmonized schema.

Today, this project is specialized, but we would like to factor out the "Prices Paid" part of this
to make it a more general tool---a "Simple Heterogeneous Data Visualizer".  You can help with that!

You might use this code as a starting point if you want to provide an API to a SOLR index but don't want to
allow direct access against SOLR for security or other reasons.

## WHAT IT DOES

This project loads a SOLR index from csv files (SolrLodr.py) and then presents a very simple API (which
really a security restricition on the SOLR web service. The main thing it does is harmonize existing 
formats (2 at present) into a single database that can be rendered. It is thus an approach to using
simple Python programs to harmonize data.  Eventually, we hope it will be used on many data sets.

In docs/example.SOLR.schema.xml is an example of the schema.xml file that I use.  This will be currently evolving.

## THE SISTER PROJECT

Although we are presenting an Api which (when hosted) will let any programmer do as they please in 
querying the haronized databases, most users will use the GUI.

The GUI is in a project called PricesPaid GUI.  That project has the best installation instructions, although this
project is completely independent of that one.  PricesPaidGUI uses PricesPaidAPI but PricesPaidAPI depends only on 
the mode P3Auth (also one of my github repos) and open-source software which I did not write, mentioned at 
PricesPaidGUI.

The easiest way to understand what PricesPaidAPI does and play with it is to install PricesPaidGUI---but that 
is not strictly necessary.

## THE PHILOSOPHY

"Embrace Chaos."  "Data Standardization is a Siren."  "Transparency trumps Standardization."
"Buyers are smart enough to understand when the data is problematic."  "Anathematize Aggregation."

But seriously, folks, the idea is to make it work as much like Google as possible.

## HOW YOU CAN HELP

* I'm a Python neophyte, this code can probably be improved.
* We need to modularize all the actual named fields to that this code could be generalized for 
some other purpose.
* We need to write a push API so that new data can be pushed rather than delivered through a 
CSV file as today.

## USING THE PROJECT

Note that abn example file exists in the "cookedData" file. In that directory you fill find the 
file FY14TX-pppifver-USASpending-5-0-0-0-1.csv.  This file 
is simply a renamed (and unchanged) export from the site USASpending.gov, in this case for 
fiscal year 2014 and the state of Texas. It contains 23K records of completely public data 
for testing this code.  Note that the "Units" field is constructed by this adapter, because
USASpending.gov does not actually contain "number of units purchased data".
 The basic approach of PricesPaidAPI at present is to read .CSV files like 
that one.  Note that name of the file follows a strict convention that defines which adapter to use.
If you would like to use this project for something else, create your own adapter, possibly using
the same filename/versioning convention.

The basic idea of this project is to have many such .csv files using many different adapters.
I would love for someone to donate an additional public data file to this project.  The Federal government has
many such files but considers them confidential.

Note that the cookedData directory in this project is NOT in the place it is configured to be
in ppcofig.example.py.  I have added it here only as an example.

  This is a small data file, but when placed in the
correct (not example) cookedData directory, will allow the execution of "python SolrLodr.py"
to load 23K records of completely public data for testing your own site.

