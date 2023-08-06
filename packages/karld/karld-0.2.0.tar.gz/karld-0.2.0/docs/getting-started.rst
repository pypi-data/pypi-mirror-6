Getting Started with karld
===========================

You have some things you want to do with some data you have.
Maybe it's in a couple of files, or one big file and you
need to clean it up and extract just part of it or maybe you also
need to merge multiple kinds of files based on a common part such
as an email address.
It's not already indexed in a database either so you can't
just do a SQL statement to get the results.
You could manipulate it with python, but putting
all the data in big dictionaries with email as the key
and then iterating over one doing lookups on the other
proves to be slow and can only be done with limited
size data.

karld is here to help. First off, the name karld was chosen
because it sounds like knarled, but it's knot.

Examples
==============================

Split a csv data file
++++++++++++++++++++++
From the example directory available by cloning the repository at https://github.com/johnwlockwood/karl_data.

Once cloned to your local system, cd into the karld project directory and run

    python setup.py install

This will install karld. Then cd into the example directory and run:

    python split_multiline.py

This will read multiline/data.csv and produce split_data_ml and split_data_ml_pipe.
Run it and compare the input and output. Checkout the source.

