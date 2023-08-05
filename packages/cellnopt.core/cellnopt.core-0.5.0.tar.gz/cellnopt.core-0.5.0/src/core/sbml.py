# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
from __future__ import print_function
#from __future__ import unicode_literals


__all__ = ["SBML"]



class SBML(object):
    """Creates SBMLQual file given 

    sbml = SBML(c, model_name="test")
    note = sbml.create_note()
    vcard = sbml.create_vcard("john", "smith")
    annotation = sbml.create_annotation(vcards = [vcard])

    

    """
    def __init__(self, data, version="1.0", model_name=None):
        self.data = data # ! a reference
        self.annotation = None
        self.note = None
        self.version = version
        self.header = None
        self.footer = None
        self.model_name = None

    def create_header(self):
        header = """<?xml version='%s' encoding='UTF-8' standalone='no'?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" qual:required="true" level="3"
xmlns:qual="http://www.sbml.org/sbml/level3/version1/qual/version1">""" % self.version
        self.header = header
        return header

    def create_model_name(self):
        self.model = """<model id="%s"> """ % self.model_name
        return self.model

    def create_compartment(self, constant="true", id="main"):
        self.compartment = """
     <listOfCompartments>
       <compartment id="%s" constant="%s"/>
     </listOfCompartments>\n""" %(id, constant)
        return self.compartment



    def create_footer(self):
        self.footer = "</sbml>"
        return self.footer

    def create_note(self, htmlcode ):
        text = """
  <notes>...
    <body xmlns="http://www.w3.org/1999/xhtml">
      %s
    </body>
  </notes>""" % htmlcode
        self.note = text
        return text

    def create_vcard(self, firstname, lastname, organism="", email=""):
        params = {
            'firstname':firstname, 'lastname':lastname,
            'organism':organism, 'email':email}

        vcard = """
              <rdf:li rdf:parseType="Resource">
                <vCard:N rdf:parseType="Resource">
                  <vCard:Family>%(lastname)s</vCard:Family>
                  <vCard:Given>%(firstname)s</vCard:Given>
                </vCard:N>
                <vCard:EMAIL>%(email)s</vCard:EMAIL>
                <vCard:ORG rdf:parseType="Resource">
                  <vCard:Orgname>%(organism)s</vCard:Orgname>
                </vCard:ORG>
              </rdf:li>""" % params
        return vcard


    def create_annotation(self, vcards=None):
        """

        """

        if vcards == None:
            raise ValueError("you must provided a list of vcards to fill the annotation")

        text = """
  <annotation>
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:vCard="http://www.w3.org/2001/vcard-rdf/3.0#">

    <rdf:Description rdf:about="my_metaid">
        <dc:creator>
            <rdf:Bag>\n"""

        for vcard in vcards:
            text += vcard + "\n"

        text += """
            </rdf:Bag>
          </dc:creator>
    </rdf:Description>
   </rdf:RDF>   
  </annotation>\n"""
        self.annotation = text
        return text
