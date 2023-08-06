Whats' new, what has changed
================================


Revision 1.2
------------------

* 1.2.6:
	* fixing bug report 22 related to KEGG.pathway2sif function that was	failing.
	* add option in biomart to use different host. This is to fix an issue where
      biomart hangs forever. This was reported by Daniel D bug report 23 on
	  assembla.


* 1.2.5: 
    * add try/except for pandas library.

* 1.2.4: 
    * fixing typo in the init that fails bioservices ito be used if pkg_resources is not available.

* 1.2.3
    * updating some apps (fasta,peptides, taxon) in bioservices.apps directory
	* Improves UniProt module by adding a dataframe export where performing a search
	* added the BioDBnet service.
	* added Pathway Common
	* fixed UniChem: add new database identifiers and fix interpretation of the output

* 1.2.2:
   * NEW Service: :class:`bioservices.biodbnet.BioDBNet`
   * uniprot: add multi_mapping method to use mapping method on large queries and
     added timeout/trials inside uniprot functions

* 1.2.1:
  * same as 1.2.0 but fixed missing mapping and apps directory in the distribution available on pypi

* 1.2.0
   * Kegg class has now an alias called KEGG
   * NEW Services: :class:`bioservices.muscle.MUSCLE`
   * fix bug in get_fasta from uniprot class
   * add aliases to quickGO to retrieve annotation
   * NEW Service: :class:`bioservices.pathwaycommons.PathwayCommons`
   * NEW Service: :class:`bioservices.geneprof.GeneProf` service
   * uniprot add function to get uniprot fasta sequence
   * add apps.peptides module

Revision 1.1
------------------

* 1.1.3
    * fix bug in chembldb.get_all_targets() that was failing to return the
	json/dictionary as expected.

* 1.1.2
    * add biocarta, pfam modules (and htmltools. maybe not required.)
	* fix bug in uniprot.mapping to return list of values instead of a string
	  (assembla ticket 19).

* 1.1.1:
    * services.py: move print statements into loggin.warning
	* add documentation and examples related to Galaxy/BioPython.
    * uniprot mapping function now returns a dictionary instead of a list
    * NEW Service : class:`bioservices.hgnc.HGNC` + doc + test

Revision 1.1
------------------
* 1.1.0:
    * in psicquic when performing the conversion, we now use a try/except since some fields (in rare case) may be missing
	* add faqs in the doc + update of the README and metadata.
	* fix typo in the list of uniprot mapping
	* Use BeautifulSoup4 instead of 3
	* add the ChEBI  Web Service.
	* add the UniChem  Web Service.
	* logging ERROR in Service when data cannot be converted to XML is now a simple warning
	* kegg.conv method now returns a dictionary instead of list of tuples.

Revision 1.0
------------------

* 1.0.4
	* 	add a draft version of PDB just to be able to fetch PDB data and use it
		with external tool such as PyMOL as shown in the new pymol.rst
	  	documentation.
	* add a missing docstring in uniprot +  check to/fr parameters in UniProt.mapping
	  method.
	* Fix a typo in PSICQUIC module.
	

* 1.0.3
    * uniprot.UniPort.search method: default value of the parameter format is now "tab"
	* fix 1 quickgo test
	* a few documentation updates in biomart/uniprot/chembldb and tutorial.

* 1.0.2:
    * add SOAPpy in the setup requirements
	* finished ArrayExpress +doc + tests
	* fixed a bug in KEGGParser.parseGene
	* add methods in psicquic to parse all databases and convert to uniprot if
      possible. These methods are used to build an application provided in the
	  tutorial
    * add biomart + doc + test
    * add onWeb method in Service class
    * add chemspider draft
	* complete eutils 

* 1.0.1
    * Add miriam module
    * Add arrayexpress 

* 1.0.0:
    * First release of bioservices

Revision 0.9
------------------

* 0.9.7: 
    * add new feature in KEgg module to instrospect kgml data sets
	* add biogrid test and documentation.
	* chembldb improvments
	* uniprot bug fixes (search if working as expected now)
* 0.9.6:
    * Finalising the Kegg module
* 0.9.5: 
    * add parser for all KEGG entries (enzyme, genome, pathway, ...) 
	* add a show_pathway to highlight element in a pathway
* 0.9.4:
    * cleaning up the modules

* 0.9.3:
    * documentation cleanup
    * fix tests
    * fix a few small bugs in biomodels 
    * adding getattr method for all databases in kegg model
    * Service class has new method call pubmed to load pubmed in browser

* 0.9.2:
    * uniprot search method improved


* 0.9.1: fix typo in biomodel. add uniprot search method. add keggParser class

* 0.9.0: Stable version of bioservices including the following services:
	BioModels, Kegg, Reactome, Chembl, PICR, QuickGO, Rhea, UniProt,
	WSDbfetch, NCBIblast, PSICQUIC, Wikipath


Up to Revision 0.5
------------------- 
* 0.4.9: finalise wikipathway
* 0.4.8: finalise doc of half of the services.
* 0.4.7: add psicquic service and carry on reactome
* 0.4.6: finalise kegg module and test
* 0.4.5: finalise biomodels. keff WSDL is not maintained anymore: started REST version. 
* 0.4.4: finalise quickgo,rhea, picr, uniprot. Update servie to use logging module.
* 0.4.3: add quickgo
* 0.4.2: add wsdbfetch/uniprot
* 0.4.1: add wikipathways module +test .
* 0.4.0: add rhea service + test. Updating the documentation.
* 0.3.0: add reactome + uniprot.
* 0.2.0: finalise biomodels and add picr service + test for biomdodel service..
* 0.1.0: add database and kegg modules + its documentation and tests


