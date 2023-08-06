====================================================================
HGVS -- Tools to Parse, Format, and Map Biological Sequence Variants
====================================================================

| Users: `PyPI <https://pypi.python.org/pypi?name=hgvs>`_ | `Documentation <http://pythonhosted.org/hgvs/>`_ | `Discuss <https://groups.google.com/forum/#!forum/hgvs-discuss>`_
| Developers: |build_status| | `Source <https://bitbucket.org/invitae/hgvs>`_ | `Issues <https://bitbucket.org/invitae/hgvs/issues?status=new&status=open>`_

This package provides a Python library to facilitate the use of genome,
transcript, and protein variants that are represented using the Human
Genome Variation Society (`HGVS`_) recommendations.

.. IMPORTANT::
   hgvs 0.2.x **requires** the uta1 interface.  Apologies to users who
   received errors with 0.1.11 due to this undocumented change.  The
   example below has been updated.  Other examples will be updated soon.
   Examples will now be written in doctest format and included in testing.


Features
-------- 

* `A formal grammar <http://pythonhosted.org/hgvs/grammar.html>`_ for HGVS variant names
* `Classes <http://pythonhosted.org/hgvs/modules.html>`_ that model HGVS
  concepts such as `Interval
  <http://pythonhosted.org/hgvs/modules.html#hgvs.location.Interval>`_,
  intronic offsets (in `BaseOffsetPosition
  <http://pythonhosted.org/hgvs/modules.html#hgvs.location.BaseOffsetPosition>`_),
  frameshifts, uncertain positions, and types of variation (`hgvs.edit
  <http://pythonhosted.org/hgvs/modules.html#module-hgvs.edit>`_)
* Formatters that generate HGVS strings from internal representations
* Tools to map variants between genome, transcript, and protein sequences
  (`HGVSMapper <http://pythonhosted.org/hgvs/modules.html#hgvs.hgvsmapper.HGVSMapper>`_ and `Projector
  <http://pythonhosted.org/hgvs/modules.html#hgvs.projector.Projector>`_)
* Reliable handling of regions reference-transcript discrepancy (requires UTA_)
* Tools to validate variants (coming soon)
* Support for alternative sources of reference and transcript mapping
  information (via BDI_)
* Extensive automated tests


An Example
----------
::

  $ mkvirtualenv hgvs-test
  (hgvs-test)$ pip install --upgrade setuptools
  (hgvs-test)$ pip install hgvs
  (hgvs-test)$ python

  >>> import hgvs.parser
  >>> hp = hgvs.parser.Parser()
  >>> hgvs_g = 'NC_000007.13:g.36561662C>T'
  >>> var_g = hp.parse_hgvs_variant(hgvs_g)
  >>> var_g
  SequenceVariant(ac=NC_000007.13, type=g, posedit=36561662C>T)

  >>> import bdi.sources.uta1, hgvs.hgvsmapper
  >>> bdi = bdi.sources.uta1.connect()
  >>> hm = hgvs.hgvsmapper.HGVSMapper( bdi, cache_transcripts=True )
  >>> var_c = hm.hgvsg_to_hgvsc( var_g, 'NM_001637.3' )
  >>> var_c
  SequenceVariant(ac=NM_001637.3, type=c, posedit=1582G>A)

There are `more examples in the documentation <http://pythonhosted.org/hgvs/examples.html>`_.


.. _HGVS: http://www.hgvs.org/mutnomen/
.. _UTA: http://bitbucket.org/invitae/uta
.. _BDI: http://bitbucket.org/invitae/bdi
.. _Invitae: http://invitae.com/


.. |build_status| image:: https://travis-ci.org/reece/hgvs-integration-test.png?branch=master
  :target: https://travis-ci.org/reece/hgvs-integration-test
  :align: middle

.. |build_status_old| image:: https://drone.io/bitbucket.org/invitae/hgvs/status.png
  :target: https://drone.io/bitbucket.org/invitae/hgvs
  :align: middle
