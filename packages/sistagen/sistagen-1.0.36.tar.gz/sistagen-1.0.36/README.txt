=====================
Simple Stat Generator
=====================


What's this?
============

Sistagen (Simple Stat Generator) is console tool that simplifies graph
plotting. It's main job is to parse configuration and call rrdtool to generate
desired graphs.

This app is kind of higher layer on rrdtool, allowing anything rrdtool allows,
but in easier to manage form.


Why?
====

RRDTool itself is great tool, but it's quite time consuming task to prepare
graph with it directly. On the other side, there are many bigger or lesser
(often all-in-one, and mostly web-oriented) applications, but they're
enforcing theirs philosophy, and having annoying "features".


How it works?
=============

At first, take a look on graph definition:

::

   echo "include templates.conf
   Graph test
      use disk-usage
      input-dir df-root" | sistagen

That would output file graph_400x100.png in current directory, containing
disk space utilization graph. Of course, you have to have df-root/ directory
with rrd files (generated with collectd - df plugin).

In this example, sistagen reads configuration from stdin. Thats because
no input files was given. You can pass as many files as you want, just by
giving they names of absolute path (TODO: describe more about pathes).

sistagen config1.conf config2.conf [...]



Installation
============

Just type:
::

   easy_install sistagen
   



Configuration
=============

Sistagen configuration consists of list of declarations and attributes.

Available declarations:
 - include ARG - load and parse configuration from another file, given
                 as ARG
 - template NAME - create new template (named NAME)
 - graph NAME - create new graph
 - theme NAME - color theme definition

Both graph and template means almost the same, with one difference:
template isn't graphed, it's only 'virtual' declaration, while all graph
declarations causes sistagen to plot them out.

Graph (and template) declarations should have some attributes. An attribute
in sistagen configuration is line, starting with at last one whitespace and 
beginning with keyword, followed by number of named values.
It's important that attribute must always refer to declaration, so:
1. all attributes that follows a declaration, belongs to that declaration
2. it's an error to pass attributes before any declaration

In its simplest case it looks like following:

::

   GRAPH|TEMPLATE name
      attribute1 name=val ...
      attribute2 ...
      ...

Most of attributes should have named values (except of 'use', 'merge' and 'size').
Each value should be in form: "name value" or "name=value" (the equation 
symbol is optional).


List of allowed attributes
--------------------------

 - use template-name - use template as current declaration base
 - merge template-name [separator=S] - merge this declaration with the one given (see: difference between merge and use)

 - colors theme-name - use theme-name as base for auto-colors
 
 - input name=NAME file=FRRDFILE ds=DS cf=CF - create new input named NAME from file RRDFILE using DS and CF
   There could be as many inputs as needed.

 - output dir=PATH file=FILE prefix=PREFIX suffix=SUFFIX mask=MASK format=FORMAT
   When using output FILE then dir, mask and format are updated automatically, but prefix and suffix are cleared

 - option option-name option-value
 - option ...
 - ...
   any option that may be passed into rrdtool graph,
   for example: lower-limit, zoom, start, etc..


 - size SIZE [SIZE, ...]
   any number of dimensions of graphs to be generated
   each size would be used in output file name


 - line1|line2|line3|area (with EXPR | use NAME) [color COLOR] [text LEGEND] [stack]
 - gprint text TEXT (with EXPR | use NAME) get AGGR
   currently supported graphing methods
   for lines and areas there should be at last one of 'with' or 'use'
   keyword with corresponding value
   EXPR means any rpn expression (http://oss.oetiker.ch/rrdtool/doc/rrdgraph_rpn.en.html)
   NAME means any input name defined earlier
   AGGR means an aggregation function (one of CF)
 - comment text TEXT 
 

Graph and template declarations may be inherited. It means that when
one declaration inherits another then all attributes of parent would
be copied into child.

Example:
::

   Template A:
      attribute a

   Template B:
      use A # use A as base
      # attribue a is defined already

      
Merge vs Use attributes
-----------------------

Use is generally used in the terms of inheritance. That means, it'll cause to copy 
all attributes from 'parent'. Also, 'use' will override any existing values.
Merge on the other side, will NOT override any values, and will copy only
input and graph declarations. 

In summary: use is used in inheritance, merge is used in combining graphs.



Output filename
---------------
Destination filename is created from several parts:
OUTPUT-DIR + OUTPUT-PREFIX + OUTPUT-MASK + OUTPUT-SUFFIX + OUTPUT-FORMAT

OUTPUT-MASK may contain several keywords, that would be replaced during graph 
generation. They are:
- %(width)i - will be replaced with current graph width
- %(height)i - as above, but height
- %(name)s - current graph (declaration) name

Default output mask looks like: _%(width)ix%(height)i


Color theme
-----------

It is possible to define a "color theme" that defines colors per 
each graph element. Each one by default uses color=auto declaration,
and in such situation sistagen pulls next available color from color 
theme (if number of graph elements outnumbers colors in color definition
- random color is generated).

In general, color theme definition looks like

::
    Theme THEME_NAME
        color value=RGBVAL [alpha=AA] [for=any|line|line123|area]
        color ...
        ...
        
Color defines new color definition, that would be used by graph elements when 
color=auto is set. It is possible to define any number of colors in theme declaration.

Available values:
 - value - color RGB or RGBA value
 - alpha - alpha value (overrides alpha part from RGBA value)
 - for - use this color only for mathing graph element (default=all)
 

Templates
=========

There are some templates already prepared and shipped with applications, that 
lets fast and easy graph creation. 
Right now they are mostly focused on rrd files created by collectd, so with 
those files you may just create graph with only input-dir attribute.

Templates dir and current dir are added to config path (-C) by default.


Collectd
--------

Right now, all of the templates defined are prepared for stats generated by 
collectd daemon.



Examples
========

Here are some example graph definitions:

::
    
    include templates.conf
    Graph cpu
        # this would graph cpu-0 usage
        use cpu
        input dir=/var/lib/collectd/rrd/localhost/cpu-0

        
::

    include templates.conf
    Graph load
        # cpu load average for 1, 5 and 15 min
        use load
        input dir=/var/lib/collectd/rrd/localhost/load

        
::

    include templates.conf
    Graph bandwidth-eth0
        # bandwidth utilization
        use bandwidth
        input dir=/var/lib/collectd/rrd/localhost/interface-eth0/
        output prefix=bw-eth0


See "examples/" directory for more.

        

.. hint::
    Please send me any reports and opinions as well. It would be nice to know
    if this tool is useful for someone, so I may still work on this. You'll 
    find my mail address in --help.
    