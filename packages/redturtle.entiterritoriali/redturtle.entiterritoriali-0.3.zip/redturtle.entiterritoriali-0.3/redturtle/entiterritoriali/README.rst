Introduction
============
This package provides vocabulary for all italian 'enti territoriali'.
For storage we are using sqlite3 database wrapped with sqlalchemy.

First lets import the vocabulary (which should have already a vocabulary object)::

    >>> from redturtle.entiterritoriali import EntiVocabulary as EV

Now let's try the simple query: for regione, provincia and comune::

    >>> EV.regione('Emilia-Romagna')
    MappedRegioni(regione=u'Emilia-Romagna',...)

    >>> EV.provincia('Ferrara')
    MappedProvince(provincia=u'Ferrara',...)

    >>> EV.comune('Ferrara')
    MappedComuni(comune_id=4105,comune=u'Ferrara',...)


Then let's check if we have all of them::

    >>> len(EV.allRegioni())
    20

    >>> len(EV.allProvince())
    108

    >>> len(EV.allComuni())
    8101


Now we can try to use `like` statesment. We can use helper methods::

    >>> EV.comuniByLetter('Mod')
    [MappedComuni(comune_id=4013,comune=u'Modena',provincia=u'MO',...u'http://www.comune.modugno.ba.it/')]

    >>> EV.provinceByLetter('Bo')
    [MappedProvince(provincia=u'Bologna',...u'http://www.provinz.bz.it/')]

    >>> EV.regioniByLetter('L')
    [MappedRegioni(regione=u'Lazio',capoluogo=u'Roma'...u'postaweb@regione.lombardia.it')]


... but you can also build your own filters using sqlalchemy and pass them as list of arguments::

    >>> sql_filter1 = (EV.engine.comuni.provincia == 'BO')
    >>> sql_filter2 = (EV.engine.comuni.comune.like('Gal%'))
    >>> EV.comuni([sql_filter1, sql_filter2])
    [MappedComuni(comune_id=4065,comune=u'Galliera',...http://www.comune.galliera.bo.it/')]


You can find more at http://www.sqlalchemy.org/docs/05/ormtutorial.html#querying

Now some more advanced querying - getting all comuni for provincia::

    >>> EV.comuni4provincia('BO')
    [MappedComuni(comune_id=4038,comune=u"Anzola dell'Emilia"...u'http://www.comune.zolapredosa.bo.it/')]

and all province for given regione::

    >>> EV.province4regione('03') #Lombardia
    [MappedProvince(provincia=u'Bergamo',...sito_provincia=u'http://www.provincia.va.it/')]


Finally we can also map vocabulary to DisplayList (for Archetypes use case)::

    >>> from redturtle.entiterritoriali.vocabulary import mapDisplayList
    >>> mapDisplayList(EV.allRegioni())
    [(u'13', u'Abruzzo'), (u'17', u'Basilicata'),...(u'05', u'Veneto')]


But it should work also for different enti in one vocabulary, like here::

    >>> regione1 = EV.regione('Lombardia')
    >>> comune1 = EV.comune('Ferrara')
    >>> enti = [regione1,comune1]
    >>> mapDisplayList(enti)
    [(u'03', u'Lombardia'), (u'038008', u'Ferrara')]


Credits
=======

Developed with the support of  `Regione Emilia Romagna`__;  Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/


Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
    :alt: RedTurtle Technology Site
    :target: http://www.redturtle.it/


Data credits
------------
* `Italian National Institute of Statistics`__

.. image:: http://en.istat.it/images/istat.gif
    :alt: ISTAT - logo

__ http://en.istat.it/
