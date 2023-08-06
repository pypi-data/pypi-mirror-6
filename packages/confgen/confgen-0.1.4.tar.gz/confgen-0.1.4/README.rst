=======
confgen
=======

.. image:: https://badge.fury.io/py/confgen.png
    :target: http://badge.fury.io/py/confgen

.. image:: https://pypip.in/d/confgen/badge.png
        :target: https://crate.io/packages/confgen?version=latest


**ConfGen** is a little command utility that will help you to generate some configurations

* Free software: BSD license
* Tested on python 2.7 and 3.2

Introduction
============

In my company, we didn't have a correct tool to generate configuration for our networking devices, just a piece 
of crappy VBA code that doesn't really fit our needs. So I started to think about a little tool that can provides
us simplicity. So, the main idea is that we often have some inputs data in an Excel file, and we use this file
to build our configurations with one template.

Quick steps to useConfGen :

* Collect your data and put it in a csv file, the first line of the file should be your title line with the name of your variables
* Build your template(s), confgen is based on ``jinja``, so if you want to build templates, just RTFD of ``jinja`` on http://jinja.pocoo.org/docs/
* Generate your file(s)

Installation
============

Linux
-----

Install setuptools : https://pypi.python.org/pypi/setuptools

At the command line

.. code-block:: console

    $ easy_install confgen

Or

.. code-block:: console

	$ pip install confgen

Windows
-------

* Download python and install python from here_
* Install setuptools : https://pypi.python.org/pypi/setuptools (save as, then double click)
* Add `;C:\pythonXX;C:\pythonXX\scripts` where ``XX`` is your python version to your environment PATH
* Open a cmd and

.. code-block:: console

	easy_install pip
	pip install confgen

Usage
=====

You have to call ``confgen`` from your command line.

Command-line options
--------------------

-a    (--append) Appending the ouput to the end of the file if it exists
-d    (--delimiter) Delimiter for your CSV formatted file, default is ;
-h    (--help) Display the help and exit
-i    (--input) Input filename of your CSV
-mo   (--multipleoutput) Generate on file per line, you must specify the name of the column where are the names of files to generate
-so   (--simpleoutput) Output file name, stdout if not specified
-t    (--template) Your template file in text and jinja2 format
-v    (--version) Display the version and exit


Examples
========

One file per line
-----------------

Here is a little example in order to understand how it works, your Excel/Calc tab is the following::

	name     	gender		    description											    beer_test		    child
	homer		man				D'oh!													yes					yeah
	marge		women			Now it's Marge's time to shine!		
	bart		boy				Ay caramba!																	yes
	lisa		girl			Trust in yourself and you can achieve anything.								yes
	maggie		baby			It's your fault I can't talk!												yes

which render in CSV format (with ``;`` for delimiter)::

	name;gender;description;beer_test;child
	homer;man;D'oh!;yes;yeah
	marge;women;Now it's Marge's time to shine!;;
	bart;boy;Ay caramba!;;yes
	lisa;girl;Trust in yourself and you can achieve anything.;;yes
	maggie;baby;It's your fault I can't talk!;;yes

So now, here is a first template example::

	Welcome {{ name }},

	You're a {{ gender }}
	Your favorite expression is : "{{ description }}" 
	{%- if beer_test %}
	You're allowed to drink beer
	{%- else %}
	/!\ You're not allowed to drink beer
	{%- endif %}

	{%- if child %}
	Children playground access : ok
	{%- endif %}

We would like to generate one file per line, the name of file will be the ``name`` column

.. code-block:: console

	natjohan~# confgen -i example.csv -t template.txt -mo name
	-----------------------------------------

	Input file : example.csv
	Template file : template.txt
	Delimiter : ; 

	-----------------------------------------

	File homer was generated 
	File marge was generated 
	File bart was generated 
	File lisa was generated 
	File maggie was generated 

	*** Good job my buddy ! 5 Files were generated ***

So now, you should have 5 files called homer, marge, bart, lisa, maggie

* homer::

	Welcome homer,

	You're a man
	Your favorite expression is : "D'oh!"
	You're allowed to drink beer
	Children playground access : ok
	
* marge::

	Welcome marge,

	You're a women
	Your favorite expression is : "Now it's Marge's time to shine!"
	/!\ You're not allowed to drink beer

* bart::
	
	Welcome bart,

	You're a boy
	Your favorite expression is : "Ay caramba!"
	/!\ You're not allowed to drink beer
	Children playground access : ok

* lisa::

	Welcome lisa,

	You're a girl
	Your favorite expression is : "Trust in yourself and you can achieve anything."
	/!\ You're not allowed to drink beer
	Children playground access : ok  

* maggie::
	
	Welcome maggie,

	You're a baby
	Your favorite expression is : "It's your fault I can't talk!"
	/!\ You're not allowed to drink beer
	Children playground access : ok

One file
--------

Now a second exemple, we just want to generate one whole file

* template.txt::

	=> {{ name }} => {{ description }}

.. code-block:: console

	natjohan~# confgen -i example.csv -t template.txt -so OneFile
	-----------------------------------------

	Input file : example.csv
	Template file : template.txt
	Delimiter : ; 

	-----------------------------------------

	*** File OneFile was generated ***

* OneFile:: 
	
	=> homer => D'oh!
	=> marge => Now it's Marge's time to shine!
	=> bart => Ay caramba!
	=> lisa => Trust in yourself and you can achieve anything.
	=> maggie => It's your fault I can't talk!

Features
========

To do
=====

* Force option open(file,'x')
* allow stdin for template
* allow to choose directory to write files

.. _here: http://www.python.org/downloads/
