===========================================
NetiNeti -- Scientific Names Discovery Tool
===========================================


Setting up VirtualEnv
=====================
  
  * install virtualenv (easy_install virtualenv or pip install virtualenv)
  
  * use the neti_env.py as the environment bootstrap (python neti_env.py ~/virtualenvs/neti)
  
  * this creates a local environment for the netineti project with all the dependencies installed
  
  * dependencies => pyyaml, nltk, nose
  
  * source ~/virtualenvs/neti/bin/activate
  
  * use netineti

Dependencies
============

  * nltk >= 2.09b3

Description
===========

Neti-Neti taxon finder.
Input: Any text preferably in English
Output: A list of Scientific Names in the text

To run it:
$ python neti-server.py

To use webservice:
$ ruby webservices/ruby/taxon_finder_web_service.rb

API:
(use your server name instead of localhost:4567)
http://localhost:4567/find?type=url&input=http://www.bacterio.cict.fr/d/desulfotomaculum.html
or
http://localhost:4567/find?type=text&input=%22Mus%20musculus%22

Files
=====

README.rst                    --- this file
src/data/black_list.txt       --- "black list" for pre filtering, common words to decrease number of false positives
src/data/white_list.txt       --- big training list, run by default
src/data/no_names.txt         --- training text w/o scientific names for negative examples
src/data/names_in_context.txt --- training list of names and these names in a context of a sentence.
src/data/test.txt             --- American Seashells book (with scientific names) for testing purposes 

src/neti_neti.py              --- Machine Learning based approach to find scientific names
src/neti_neti_helper.py       --- miscellaneous helper functions
src/neti_neti_trainer.py      --- Scientific Name classifier -- given a name-like string it accepts or rejects it as a scientific name


Usage
=====

Using from (phyton) server:

  from netineti import *

  # for long training set, about 20 min on slow machine
  nnt = NetiNetiTrain()
  # you can use other training text if you supply it as an argument:
  # nnt = NetiNetiTrain("species_train.txt")

  nn = NetiNeti(nnt)

Example Urls to try:
====================

New Species
-----------
http://www.sciencedaily.com/news/plants_animals/new_species/

http://www.livescience.com/environment/top-10-new-species-1.html

http://www.sciencedaily.com/releases/2010/04/100407104032.htm

http://species.asu.edu/2009_species05

BHL BOOKS
---------
http://ia311319.us.archive.org/3/items/americanseashell00abbo/americanseashell00abbo_djvu.txt

http://ia341016.us.archive.org/3/items/britishinsectsge00westuoft/britishinsectsge00westuoft_djvu.txt



Note: offsets do not work in this version.

