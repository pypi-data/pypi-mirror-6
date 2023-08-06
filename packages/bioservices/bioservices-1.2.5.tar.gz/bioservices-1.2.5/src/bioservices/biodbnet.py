#!/usr/bin/python
# -*- coding: latin-1 -*-
#
#  This file is part of bioservices software
#
#  Copyright (c) 2011-2013 - EBI-EMBL
#
#  File author(s):
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
#$Id: biodbnet.py 323 2014-03-24 12:54:46Z cokelaer $
"""This module provides a class :class:`~BioDBNet` to access to BioDBNet WS.


.. topic:: What is BioDBNet ?

    :URL: http://biodbnet.abcc.ncifcrf.gov/
    :Service: http://biodbnet.abcc.ncifcrf.gov/webServices
    :Citations:  Mudunuri,U., Che,A., Yi,M. and Stephens,R.M. (2009) bioDBnet: the biological database network. Bioinformatics, 25, 555-556

    .. highlights::

        "BioDBNet Database is a repository hosting computational models of biological
        systems. A large number of the provided models are published in the
        peer-reviewed literature and manually curated. This resource allows biologists
        to store, search and retrieve mathematical models. In addition, those models can
        be used to generate sub-models, can be simulated online, and can be converted
        between different representational formats. "

        -- From BioDBNet website, Dec. 2012

    .. versionadded:: 1.2.3
    .. sectionauthor:: Thomas Cokelaer, Feb 2014

"""
from bioservices.services import WSDLService
import SOAPpy

__all__ = ["BioDBNet"]


class BioDBNet(WSDLService):
    """Interface to the `BioDBNet <http://biodbnet.abcc.ncifcrf.gov/>`_ service

    ::

        >>> from bioservices import *
        >>> s = BioDBNet()

    Most of the BioDBNet WSDL are available. There are functions added to
    the original interface such as :meth:`extra_getReactomeIds`.

    Use :meth:`db2db` to convert from 1 database to some databases.
    Use :meth:`dbReport` to get the convertion from one database to all
    databases.

    """
    _url = 'http://biodbnet.abcc.ncifcrf.gov/webServices/bioDBnet.wsdl'
    def __init__(self, verbose=True):
        """.. rubric:: Constructor

        :param bool verbose:

        """
        super(BioDBNet, self).__init__(name="BioDBNet", url=BioDBNet._url, verbose=verbose)

    def _interpret_input_db(self, inputValues):
        if isinstance(inputValues, list):
            inputValues = ",".join(inputValues)
            return inputValues
        elif isinstance(inputValues, str):
            return inputValues
        else:
            raise NotImplementedError

    def _interpret_output_db(self, input_db, output_db):
        if isinstance(output_db, list):
            outputs = ",".join(output_db)
        else:
            outputs = output_db
        inputResult = self.getInputs()
        #getOutputsForInput method
        outputResult = self.getOutputsForInput(input_db)
        for output in outputs.split(","):
            if output not in outputResult:
                print(output + " not found")
                print(outputResult)
                raise Exception
        return outputs



    def db2db(self, input_db, output_db, inputValues, taxon=9606):
        """Retrieves the models which are associated to the provided Taxonomy text.

        :param str text: free (Taxonomy based) text
        :return:  list of model identifiers

        ::

            >>> from bioservices import BioDBNet
            >>> input_db = 'Ensembl Gene ID'
            >>> output_db = ['Gene Symbol']
            >>> input_values = ['ENSG00000121410, ENSG00000171428']
            >>> print(s.db2db(input_db, output_db, input_values, 9606)
            Ensembl Gene ID Gene Symbol
            ENSG00000121410 A1BG
            ENSG00000171428 NAT1

        """
        inputValues = self._interpret_input_db(inputValues)
        outputs = self._interpret_output_db(input_db, output_db)

        #dbPath = 'Ensembl Gene ID->Gene ID->Homolog - Mouse Gene ID->Ensembl Gene ID'
        #getDirectOutputsForInput method
        #directOutputResult = self.getDirectOutputsForInput(input_db)

        #db2db method
        if taxon:
            taxonId = str(taxon)
            params = SOAPpy.structType({'input': input_db, 'inputValues':
                inputValues, 'outputs': outputs, 'taxonId': taxonId})
        else:

            params = SOAPpy.structType({'input': input, 'inputValues':
                inputValues, 'outputs': outputs, 'taxonId': ''})

        res = self.serv.db2db(params)
        return res

    def dbFind(self, input_db, inputValues, taxon="9606"):
        inputValues = self._interpret_input_db(inputValues)
        taxonId = str(taxon)
        params = SOAPpy.structType({'input': input_db, 'inputValues':
            inputValues, 'taxonId': taxonId})
        return self.serv.dbFind(params)


    def dbOrtho(self, input_db, output_db, inputValues, input_taxon, output_taxon):
        raise NotImplementedError
        inputValues = self._interpret_input_db(inputValues)
        outputs = self._interpret_output_db(input_db, output_db)

        taxon1 = str(input_taxon)
        taxon2 = str(output_taxon) # could be a list ?

        params = SOAPpy.structType({'input': input, 'output': output,
            'inputValues': inputValues,  'inputTaxon': taxon1, 'outputTaxon':
            taxon2})

        return self.serv.dbOrtho(params)

    def dbReport(self, input_db, inputValues, taxon=9606, output="raw"):
        """Returns report

        :param output: returns dataframe if set to dataframe

        ::

            s.dbReport("Ensembl Gene ID", ['ENSG00000121410', 'ENSG00000171428'])


        """
        inputValues = self._interpret_input_db(inputValues)
        taxonId = str(taxon)
        params = SOAPpy.structType({'input': input_db, 'inputValues':
            inputValues, 'taxonId': taxonId})
        res = self.serv.dbReport(params)
        if output == "dataframe":
            try:
                import pandas as pd
            except:
                print("Pandas library is not installed. dataframe are not  available")
            import StringIO
            df = pd.readcsv(stringIO.StringIO(res.strip()), sep="\t")
            return df
        else:
            return res

    def dbWalk(self , dbPath, inputValues, taxon=9606):
        dbPath = 'Ensembl Gene ID->Gene ID->Homolog - Mouse Gene ID->Ensembl Gene ID'
        inputValues = self._interpret_input_db(inputValues)
        taxonId = str(taxon)
        params = SOAPpy.structType({'dbPath': dbPath, 'inputValues':
            inputValues, 'taxonId': taxonId})
        return self.serv.dbWalk(params)

    def getDirectOutputsForInput(self, input_db):
        return self.serv.getDirectOutputsForInput(input_db).split(",")

    def getInputs(self):
        """Return list of possible input database

        ::

            s.getInputs()
        """
        return self.serv.getInputs().split(",")

    def getOutputsForInput(self, input_db):
        """Return list of possible output database for a given input database

        ::

            s.getOutputsForInput("UniProt Accession")

        """
        if input_db not in self.getInputs():
            raise ValueError("Invalid input database provided")
        return self.serv.getOutputsForInput(input_db).split(",")



