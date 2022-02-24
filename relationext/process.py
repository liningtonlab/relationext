from doctest import OutputChecker
import json
import re
import ast
from enum import unique
from os import EX_SOFTWARE
from taxonerd import TaxoNERD
import nltk
import pkg_resources as pkr

from .organism_categorizer import taxonerd_df_to_dict, replace_org_in_abstract
from .compound_name_extractor import chem_ner_prototype, get_compound
from .relation_extractor import get_relation


nltk.download()

SOURCE_ORGANISM_REGEX = "[A-Z]{1}[a-z]+ {1}[a-z]+\.? ?[A-Z0-9-]+ ?[A-Z]?[a-zA-Z0-9-]+|[A-Z]{1}[a-z]+ {1}[a-z]+\.?"
# https://regexr.com/60t8c

ner = TaxoNERD(model="en_ner_eco_biobert", prefer_gpu=False,
                   with_abbrev=False)

# Returns Taxonerd result for an abstract.
def get_proper_entity_list(abstract):
    proper_entity_list = []
    taxon = ner.find_entities(abstract)
    entity = taxon.to_json(orient='records', lines=True)
    entities = entity.splitlines()

    print(entities)

    if entities == ['']:
        return None

    for ent in entities:
        string_dict_to_dictionary = json.loads(ent)
        if re.search(SOURCE_ORGANISM_REGEX, string_dict_to_dictionary["text"]):
            proper_entity_list.append(ast.literal_eval(ent))

    return proper_entity_list


def get_relations(abstract):

    # added to deploy package
    resource_name = pkr.resource_filename('relationext', 'data/root_name_list.txt')

    with open(resource_name) as file:
        lines = file.readlines()
        root_name_list = [line.rstrip() for line in lines]
        root_name_list = root_name_list + [x.lower() for x in root_name_list]
        # print(root_name_list)
    
    if isinstance(abstract, str):
            
        proper_entity_list = get_proper_entity_list(abstract)
        if proper_entity_list is None:
            return "No Compounds Found"

        source_list = taxonerd_df_to_dict(proper_entity_list)

        new_abstract = replace_org_in_abstract(abstract, proper_entity_list)

        chem_list_by_ner = chem_ner_prototype(new_abstract)
        chem_list_by_root = get_compound(new_abstract, root_name_list)

        rel_by_ner = get_relation(chem_list_by_ner, source_list, new_abstract)
        rel_by_root = get_relation(chem_list_by_root, source_list, new_abstract)
        unique_rel = [dict(t) for t in {tuple(d.items()) for d in rel_by_ner+rel_by_root}]

        return unique_rel
