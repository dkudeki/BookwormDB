[![Travis Build Status](https://travis-ci.org/Bookworm-project/BookwormDB.svg?branch=master)](https://travis-ci.org/Bookworm-project/BookwormDB)

[BookwormDB](https://github.com/bookworm-project/BookwormDB "BookwormDB") is the main code repository for the Bookworm project. Given simply formatted files and metadata, it creates an efficient and easily queryable MySQL database that can make full use of all the metadata and lexical data in the original source. It also includes a powerful API for asking a variety of unigrammatic queries about that data.

A quick walkthrough is included below: other documentation is at [bookworm.culturomics.org]() and in a [Bookworm Manual](http://bookworm-project.github.io/Docs) on this repository (editable at the repo [here](https://github.com/Bookworm-project/Docs)).

# Installation

Installation is tested on Ubuntu and OS X. It may work on other Unixes, but will probably not work on Windows.

1. Install some dependencies; mysql or mariadb for databases.
2. Download the latest release, either by cloning this git repo or downloading a zip.
3. Navigate to the folder in the terminal, and type `pip install .`.
4. Type `bookworm --help` to confirm the executable has worked. If this doesn't work, file
   a bug report.
5. (No longer?) Type `bookworm config mysql` for some interactive prompts to allow Bookworm to edit MySQL databases on your server. (Note that this makes some other changes to your mysql configuration files; you may want to copy them first if you're using it for other things.)

## Releases

The `master` branch is regularly tested on Travis; you are generally best off installing the latest version.

## Related projects

This builds a database and implements the Bookworm API on particular set of texts.

Some basic, widely appealing visualizations of the data are possible with the Bookworm [web app](https://github.com/bookworm-project/BookwormGUI "Bookworm web app"), which runs on top of the API. 

A more wide-ranging set of visualizations is available built on top of D3 in the [Bookworm D3 package](http://github.com/bmschmidt/BookwormD3).
If you're looking to develop on top of Bookworm, that presents a much more flexible set of tools.

## Bookworms ##
Here are a couple of Bookworms built using [BookwormDB](https://github.com/bookworm-project/BookwormDB "Bookworm"):

1. [Open Library](http://bookworm.culturomics.org/OL/ "Open Library")
2. [ArXiv](http://bookworm.culturomics.org/arxiv/ "ArXiv")
3. [Chronicling America](http://arxiv.culturomics.org/ChronAm/ "Chronicling America")
4. [SSRN](http://bookworm.culturomics.org/ssrn/ "SSRN: Social Science Research Network")
5. [US Congress](http://bookworm.culturomics.org/congress/ "Bills in US Congress")
6. [Rate My Professor Gendered Language](http://benschmidt.org/profGender)


## Getting Started ##

### Required MySQL Database ###

You must have a MySQL database set up that you can log into with admin access,
probably with a `my.cnf` file at ~/.my.cnf.

Bookworm will automatically create a select-only user that handles web queries,
preventing any malicious actions through the API. 


## The query API

This distribution also includes two files, general_api.py and SQLapi.py, which together constitute an implementation of the API for Bookworm, written in Python. It primarily implements the API on a MySQL database now, but includes classes for more easily implementing it on top of other platforms (such as Solr).

It is used with the [Bookworm GUI](https://github.com/Bookworm-project/BookwormGUI) and can also be used as a standalone tool to query data from your database. To run the API in its most basic form, type `bookworm query $string`, where $string is a json-formatted query.


While the point of the command-line tool `bookworm` is generally to *create* a Bookworm, the point of the query API is to retrieve results from it.

For a more interactive explanation of how the GUI works, see the [Vega-Bookworm project sandbox].
Walkthrough
===========

These are some instructions on how to build a bookworm. 

We'll use a collection of 450 novels in 3 languages:

Piper, Andrew (2016): txtlab Multilingual Novels. figshare.

### Download and unzip the files.

```
wget https://ndownloader.figshare.com/files/3686805
wget https://ndownloader.figshare.com/files/3686778
unzip 3686778

```
### Create catalog and text files.

For this set, a simple python script suffices to build the 
two needed files, using the textlab's files. Paste this into parse.py

```python
import pandas as pd
import json
output = open("input.txt", "w")
catalog = open("jsoncatalog.txt", "w")
for book in pd.read_csv("3686805").to_dict(orient="records"):
    try:
        fulltext_lines = open(f"2_txtalb_Novel450/{book['filename']}").readlines()
        # Bookworm reserver newline and tab characters, so they are stripped before
        fulltext = "\f".join(fulltext_lines)
        fulltext = fulltext.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        book['filename'] = str(book['id'])
        output.write(f"{book['filename']}\t{fulltext}\n")
        book['searchstring'] = book['title'] + ' ' + book['author']
        catalog.write(json.dumps(book) + "\n")
    except FileNotFoundError:
        # This dataset has errors!
        continue
```

```sh
python parse.py
```

Then Create a bookworm.cnf file in the file. (This isn't always necessary; usually
it can just infer the database name from your current directory.)
```
echo "[client]\ndatabase=txtlab450" > bookworm.cnf
```

### Initialize the Bookworm

```
bookworm init
bookworm build all
```
### Required files

#### Required files 1: full text of each file with an identifier.

* `input.txt`

In this format, each line consists of the file's unique identifier, followed by a tab, followed by the **full text** of that file. Note that you'll have to strip out all newlines and returns from original documents. In the event that an identifier is used twice, behavior is undefined.

By changing the makefile, you can also do some more complex substitutions. (See the metadata parsers for an example of a Bookworm that directly reads hierarchical, bzipped directories without decompressing first).

#### Required files 2: Metadata about each file.

*  `jsoncatalog.txt` with one JSON object per line. The keys represent shared metadata for each file: the values represent the entry for that particular document. There should be no new line or tab characters in this file.

In addition to the metadata you choose, two fields are required:

1. A `searchstring` field that contains valid HTML which will be served to the user to identify the text.
   * This can be a link, or simply a description of the field. If you have a URL where the text can be read, it's best to include it inside an <a> tag: otherwise, you can just put in any text field you want in the process of creating the jsoncatalog.txt file: something like author and title is good.
  
2. A `filename` field that includes a unique identifier for the document (linked to the filename or the identifier, depending on your input format).

**Note that the python script above does both of these at once.**

#### Required Files 3: Metadata about the metadata.

Now create a file in the `field_descriptions.json` which is used to define the type of variable for each variable in `jsoncatalog.txt`.

Currently, you **do** have to include a `searchstring` definition in this, but **should not** include a filename definition.


## Running ##

For a first run, you just want to use `bookworm init` to create the entire database (if you want to rebuild parts of a large bookworm--the metadata, for example--that is also possible.)

```
bookworm init
```

This will walk you through the process of choosing a name for your database.

Then to build the bookworm, type

```
bookworm build all
```

Depending on the total number and average size of your texts,
this could take a while. Sit back and relax.

Finally, you want to implement the API and see some results.

Type 

```
bookworm serve
```

To start a process on port 10012 that responds to queries.
This daemon must run continuously.

Then you can access query results over http. Try visiting this page in a web browser.

`http://localhost:10012/?q={%22database%22:%22txtlab450%22,%22method%22:%22data%22,%22format%22:%22csv%22,%22groups%22:[%22date%22,%20%22language%22],%22counttype%22:[%22TextCount%22,%22WordCount%22]}`


Once this works, you can set up an HTML query to visit this. See 
the (currently underdeveloped) Bookworm-Vega repository for some examples.
