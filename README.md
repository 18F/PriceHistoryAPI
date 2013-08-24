PricesPaidAPI
=============

Backend and web service for searching a database imported from CSV files (someday generally, but Prices Paid for now.)

INTRODUCTION

This is a project written by Robert L. Read, Martin Ringlein, Aaron Snow, and Gregory Godbout, who are all 
Presidential Innovation Fellows (Round 2).  The purpose is to save the Federal Government money by
providing a research tool that shows prices actually paid for commodities and perhaps services.  This is
completely analogous to market research that any buyer would do, although of course other avenues of 
market research should be used as well.

STATUS

Robert L. Read is the main engineer on this project, and has been working about 7 weeks on it as of August
24th.  It is now in demo-prototype mode, and is moving toward a pilot launch of 100 buyers within the
government.  At the time of this writing it is probably not documented well enough to use easily, though
of course I will respond <read.robert@gmail.com> to any questions.

This code is therefore at present quite specialized, and is unlikely to be valuable to anybody not directly
interested in the project, except perhaps as an example.

WHY YOU MIGHT CARE

Today, this project is highly specialized, but we would like to factor out the "Prices Paid" part of this
to make it a more general tool---a "Simple Heterogeneous Data Visualizer".  You can help with that!

If you are interested in using SOLR from python, this might be valuable as an example.

WHAT IT DOES

This project loads a SOLR index from csv files (SolrLodr.py) and then presents a very simple API (which
really a security restricition on the SOLR web service. The main thing it does is harmonize existing 
formats (2 at present) into a single database that can be rendered. It is thus an approach to using
simple Python programs to harmonize data.  Eventually, we hope it will be used on many data sets.

THE SISTER PROJECT

Although we are presenting an Api which (when hosted) will let any programmer do as they please in 
querying the haronized databases, most users will use the GUI.

The GUI is in a project called PricesPaid GUI which has not yet been loaded to GitHub, though I 
hope to do so soon.

THE PHILOSOPHY

"Embrace Chaos."  "Data Standardization is a Siren."  "Transparency trumps Standardization."
"Buyers are smart enough to understand when the data is problematic."  "Anathematize Aggregation."

But seriously, folks, the idea is to make it work as much like Google as possible.

HOW YOU CAN HELP

*) I'm a Python neophyte, this code can probably be improved.
*) We need to modularize all the actual named fields to that this code could be generalized for 
some other purpose.
*) We need to write a push API so that new data can be pushed rather than delivered through a 
CSV file as today.
*) I'm actively trying to make the search more useful by allowing search of every field.  I think
I know how to do this, so if you tackle this you are probably duplicating my effort---but hey, 
nature works by lots of duplication of effort.

WHY THIS CODE WILL BE HARD TO USE AT PRESENT

*) I haven't uploaded the configuration.py file that is needed.
*) I haven't given you installation instructions.
*) The sister project which uses it is not available yet.
*) I haven't uploaded any sample data.

