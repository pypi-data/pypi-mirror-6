# -*- python -*-
#
#  This file is part of bioservices software
#
#  Copyright (c) 2011-2013 - EBI-EMBL
#
#  File author(s):
#      Thomas Cokelaer <cokelaer@ebi.ac.uk>
#      https://www.assembla.com/spaces/bioservices/team
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: https://www.assembla.com/spaces/bioservices/wiki
#  documentation: http://packages.python.org/bioservices
#
##############################################################################
#$Id: picr.py 190 2013-04-17 13:37:12Z cokelaer $
"""This module provides a class :class:`~bioservices.picr.PICR` that allows an
access to the REST interface of the PICR web service. There is also a SOAP web service but we implemented only the REST interface since they both provide access to the same functionalities.

.. topic:: What is PICR ?

    :URL: http://www.ebi.ac.uk/Tools/picr
    :REST: http://www/ebi.ac.uk/Tools/picr/rest
    :Citations: http://www.biomedcentral.com/1471-2105/8/401


    .. highlights::

        "The Protein Identifier Cross-Reference (PICR) service is a web application
        that provides interactive and programmatic (SOAP and REST) access to a mapping
        algorithm based on 100% sequence identity to proteins from over 98 distinct
        source databases. Mappings can be limited by source database, taxonomic ID and
        activity status in the source database. Users can copy/paste or upload files
        containing protein identifiers or sequences in FASTA format to obtain mappings
        using the interactive interface. "

        -- From the PICR home page, Dec 2012


"""
from services import RESTService
import xmltools


__all__ = ["PICR"]
#//the NEWT taxonomy ID to limit the mappings to
#//can be null or a number. Do not specify 0 for null.
#String taxonID = "9606";     //H. Sapiens


class PICR(RESTService):
    """Interface to the `PICR (Protein Identifier Cross reference) <http://www.ebi.ac.uk/Tools/picr/>`_ service

    .. doctest::

        >>> from bioservices import PICR
        >>> p = PICR()
        >>> res = p.getMappedDatabaseNames() # get list of valid database
        >>> results = p.getUPIForSequence(p._sequence_example, \
                ["IPI", "ENSEMBL", "SWISSPROT"])


    """
    _sequence_example="MDSTNVRSGMKSRKKKPKTTVIDDDDDCMTCSACQSKLVKISDITKVSLDYINTMRGNTLACAACGSSLKLLNDFAS"
    _blastfrag_example="MSVMYKKILYPTDFSETAEIALKHVKAFKTLKAEEVILLHVIDEREIKKRDIFSLLLGVAGLNKSVEEFENELKNKLTEEAKNKMENIKKELEDVGFKVKDIIVVGIPHEEIVKIAEDEGVDIIIMGSHGKTNLKEILLGSVTENVIKKSNKPVLVVKRKNS"
    _accession_example = "P29375"
    _url = "http://www.ebi.ac.uk/Tools/picr/rest"

    def __init__(self, verbose=False):
        """.. rubric:: Constructor

        :param bool verbose: prints informative messages (default is False)

        """
        super(PICR, self).__init__(name="PICR", url=PICR._url, verbose=verbose)
        self._databases = None

    def getMappedDatabaseNames(self):
        """Returns names of the databases

        :returns: An XML containing the databases available.

        .. seealso:: :attr:`databases` to obtain a human readable list
        """
        url = self.url + "/getMappedDatabaseNames"
        res = self.request(url)
        return res

    def _get_databases(self):
        if self._databases == None:
            res = self.getMappedDatabaseNames()
            self._databases = [a.text for a in res.getchildren()]
        return self._databases
    databases = property(_get_databases, 
        doc="Get a human-readable list of databases (obtained from XML returned by :meth:`getMappedDatabaseNames`)")

    def getUPIForSequence(self, sequence, database, taxid=None,
        onlyactive=True, includeattributes=False):
        """Get Protein identifier given an exact sequence

        :param sequence: the sequence to map [required]
        :param database: the database to map to. At least one database is required, but
            multiple databases can be queried at once.
        :param taxid: the NEWT taxon ID to limit the mappings [optional]
        :param onlyactive: if true, only active mappings will be returned.
            If false, results may include deleted mappings. [optional, default is true]
        :param includeattributes: if true, extra attributes such as sequence and taxon
            IDs will be returned if available. If false, no extra information returned.
            [optional, default is false]

        .. note:: Parameter names are case sensitive.

        .. note:: Some servers, browsers and other clients may have restrictions on the length of
            the query string, so long sequences might cause errors. If this is the case, use
            a POST request rather than a GET.

        .. note:: If a taxid is submitted, includeattributes will be true.

        .. doctest::

            >>> from bioservices import PICR
            >>> p = PICR()
            >>> sequence = p._sequence_example
            >>> databases = ["IPI", "ENSEMBL", "SWISSPROT"]
            >>> results = p.getUPIForSequence(sequence, databases)

        """
        url = self._url + "/getUPIForSequence"

        # check validity of the database provided

        url += "?sequence=" + sequence
        if isinstance(database,str):
            self._checkDBname(database)
            url+= "&database=" + database
        elif isinstance(database,list):
            for d in database:
                self._checkDBname(d)
                url+="&database=" + d
        #if taxid!=None or onlyactive==False or includeattributes==False:
        #    raise NotImplementedError
        if taxid:
            url += "&taxonid=" +taxid
        if includeattributes == False:
            url += "&includeattributes=false"
        if onlyactive == False:
            url += "&onlyactive=false"


        res = self.request(url)
        return res

    def _checkDBname(self, db):
        if db not in self.databases:
            raise ValueError("Provided database name (%s) is not valid. Use database attribute to check the valid names" % db)

    def getUPIForAccession(self, accession, database,
        taxid=None,
        version=None,
        onlyactive=True,
        includeattributes=True):
        """Get Protein identifier given an accession number

        :param str accession:  the accession to map [required]
        :param str version: the version of accession to map [optional]
        :param database: the database to map to (string). At least one database is
            required, but multiple databases can be queried at once using a list.
        :param taxid: the NEWT taxon ID to limit the mappings [optional]
        :param bool onlyactive: if true, only active mappings will be returned. If false,
            results may include deleted mappings. [optional, default is true]
        :param bool includeattributes: if true, extra attributes such as sequence
            and taxon IDs will be returned if available. If false, no extra
            information returned. [optional, default is false]

        .. note:: parameter names are case sensitive

        .. note:: If version is not specified but the accession is of the form P29375.1,
            the accession and version will automatically be split to accession=P29375
            and version-1.

        .. note:: If a taxid is submitted, includeattributes will be true.

        Example:

        ::

            >>> from bioservices import *
            >>> s = PICR()
            >>> s.getUPIForAccession("P29375", ["IPI", "ENSEMBL"])
            >>> s.getUPIForAccession("P29375-1", ["IPI", "ENSEMBL"])
        """

        url = self.url + "/getUPIForAccession?accession=" + accession
        if isinstance(database,str):
            self._checkDBname(database)
            url+= "&database=" + database
        elif isinstance(database,list):
            for d in database:
                self._checkDBname(d)
                url+="&database=" + d
        if taxid:
            url += "&taxonid=" +taxid
        if includeattributes == False:
            url += "&includeattributes=false"
        if onlyactive == False:
            url += "&onlyactive=false"
        res = self.request(url)
        return res

    def getUPIForBLAST(self, blastfrag, database,
        taxid=None,
        version=None,
        onlyactive=True,
        includeattributes=False, **kargs):
        """Get Protein identifier given a sequence similarity (BLAST)

        :param str blastfrag:  the AA fragment to map [required]
        :param str database: the database to map to. At least one database is
            required, but multiple databases can be queried at once using a list.
        :param taxid: the NEWT taxon ID to limit the mappings [optional]
        :param bool onlyactive: if true, only active mappings will be returned. If false,
            results may include deleted mappings. [optional, default is true]
        :param bool includeattributes: if true, extra attributes such as sequence
            and taxon IDs will be returned if available. If false, no extra
            information returned. [optional, default is false]


        Other options (related to BLAST analysis) can be provided as optional
        argument. See this link for details:

            http://www.ebi.ac.uk/Tools/picr/RESTDocumentation.do

        As an example, you can provide the matrix argument:

        :param str matrix: specifies which protein scoring matrix to use. [optional, defaults to BLOSUM62]

        .. note:: Parameter names are case sensitive.
        .. note:: If version is not specified but the accession is of the form P29375.1,
            the accession and version will automatically be split to accession=P29375
            and version-1.

        .. note:: If a taxid is submitted, includeattributes will be true.


        ::

            >>> res = s.getUPIForBLAST(s._blastfrag_example, "SWISSPROT")
            >>> res = s.getUPIForBLAST(s._blastfrag_example, "SWISSPROT",
                   program="blastp", matrix="BLOSUM80")

        """
        url = "http://www.ebi.ac.uk/Tools/picr/rest/getUPIForBLAST"
        url += "?blastfrag=" + blastfrag
        if isinstance(database,str):
            self._checkDBname(database)
            url+= "&database=" + database
        elif isinstance(database,list):
            for d in database:
                self._checkDBname(d)
                url+="&database=" + d
        if taxid:
            url += "&taxonid=" +taxid
        if includeattributes == False:
            url += "&includeattributes=false"
        if onlyactive == False:
            url += "&onlyactive=false"

        if kargs:
            postData = self.urlencode(kargs)
            res = self.request(url + "&" +postData)
        else:
            res = self.request(url)

        return res



"""
Parameters:

    BLAST search parameters: These should not be changed unless you are sure that you know what you are doing.
        filtertype - which parameters should the BLAST results be filtered by, valid values are ORGANISM, IDENTITY, ORGANISM_AND_IDENTITY, and NONE. [optional, defaults to NONE]
            identityvalue - the minimum score to accept as a BLAST hit. [required if filtertype is IDENTITY or ORGANISM_AND_IDENTITY]
            identitytaxon - the target organism that BLAST is filtering for. [required if filtertype is ORGANISM or ORGANISM_AND_IDENTITY]
        program - which BLAST program to use for mapping [optional, defaults to blastp]
        alignments - specifies the number of alignments to find pre-filtering (there is probably no need to change this.) [optional, defaults to 100]
        scores - sets the maximum number of scores to display in output. [optional, defaults to 100]
        exp - sets the E-value cutoff. [optional, defaults to 10]
        dropoff - Amount score must drop before extension of hits is halted. [optional, defaults to 0]
        gapopen - sets the gap opening penalty. [optional, defaults to 11]
        gapext - sets the gap extension penalty [optional, defaults to 1]
        gapalign - perform gapped alignment. [optional, defaults to true]
        filter - specifies filters to be used to mask query sequence. See table 3.2.7 for details. [optional, defaults to F, ie none]
        align - sets the alignment view. [optional, defaults to 0]
        stype - sets the type of submission. [optional, defaults to protein]
        blastdb - set the database against which to query the protein fragments. [optional, defaults to uniprotkb]

"""
