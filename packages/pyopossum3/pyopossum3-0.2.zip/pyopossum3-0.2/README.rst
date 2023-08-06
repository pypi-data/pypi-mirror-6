=====================================================================================
SQLAlchemy-based interface to the oPOSSUM3 transcription factor binding site database
=====================================================================================

.. image:: https://travis-ci.org/konstantint/pyopossum3.png?branch=master   :target: https://travis-ci.org/konstantint/pyopossum3

The package provides an object-oriented access interface to the `oPOSSUM3 <http://opossum.cisreg.ca/oPOSSUM3/>`_ raw database tables.

Installation
------------

The simplest way to install the package is via ``easy_install`` or ``pip``::

    $ easy_install pyopossum3

Dependencies
------------

- ``SQLAlchemy``
- ``PyMySQL`` or any other `SQLAlchemy-compatible MySQL connector <http://docs.sqlalchemy.org/en/rel_0_9/dialects/mysql.html>`_.

Usage
-----
A usage example is the following::

   >>> from pyopossum3 import Opossum
   >>> o = Opossum("mysql+pymysql://opossum_r:@opossum.cmmt.ubc.ca/oPOSSUM3_human")
   >>> o.ConservedTfbs.query.first().gene
   >>> o.ExternalGeneId.query.filter(o.ExternalGeneId.external_id.in_(['TSPAN6'])).filter(o.ExternalGeneId.gene.has(chr='X')).first().gene
   ... etc ...

The second line creates a connection to the oPOSSUM server, and the third/fourth query the ``conserved_tfbss`` and ``external_gene_ids`` tables using SQLAlchemy syntax.

Naturally, for heavy analyses, you are suggested to set up your own copy of the database.
See `here <http://opossum.cisreg.ca/oPOSSUM3/download.html>`_ for instructions on how to download the data.

You can get a feeling for the structure of the database by running the following::

    >>> for cls in o.all_orm_classes:
    >>>    print cls.query.first()

The main table you should probably care about is ``ConservedTfbs``, which contains matches in the vicinity of each gene, annotated with match score and conservation level.

An example using the ``ucscgenome`` package to verify that TFBS sequences are indeed correct::
    
    >>> c = o.ConservedTfbs.query.filter(o.ConservedTfbs.strand==1).first()
    >>> c.gene.chr, c.absolute_start, c.absolute_end, c.seq
    ('X', 99890235L, 99890253L, 'AGAAACATTGCATACTGC')
    >>> from ucscgenome import Genome
    >>> g = Genome('hg19')
    >>> g['chrX'][99890235:99890253]
    'AGAAACATTGCATACTGC'

Note
----
The author of this package is not associated with the creators and maintainers of the oPOSSUM3 tool.

See also
--------

* Report issues and submit fixes at Github: https://github.com/konstantint/pyopossum3

