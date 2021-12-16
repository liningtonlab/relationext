import re
import nltk
import spacy
from nltk.data import retrieve
from nltk import Tree
from numpy.lib.utils import source
from spacy.tokens import Doc
from collections import OrderedDict

nlp = spacy.load('en_core_web_sm')
# nltk.download('punkt')

RELATION1 = ["isolate", "identify", "obtain", "discover", "yield", "characterize", "characterise", "produce", "purify", "saponify", "elucidate", "give", "afford", "separate", "contain", "generate", "reveal", "characterise", "provide", "furnish", "ascribe", "return", "establish"]
RELATION2 = ["isolates", "identifies", "obtains", "discovers", "yields", "characterizes", "characterises", "produces", "purifies", "saponifies", "elucidates", "gives", "affords", "separates", "contains", "generates", "reveals", "characterises", "provides", "furnishes", "ascribes", "returns", "establishes"]
RELATION3 = ["isolated", "identified", "obtained", "discovered", "yielded", "characterized", "characterised", "produced", "purified", "saponified", "elucidated", "gave", "given", "afforded", "separated", "contained", "generated", "revealed", "characterised", "provided", "furnished", "ascribed", "returned", "established", "determined"]
RELATION4 = ["isolation", "identification", "obtain", "discovery", "yield", "characterization", "characterisation", "production", "purification", "saponification", "elucidatation", "giving", "separation", "detection", "generation", "conversion", "reveal", "characterisation", "accumulation"]
MICRO_HIGHER_RELATION = ["isolated", "identified", "obtained", "discovered", "yielded", "characterized", "characterised", "produced", "purified", "saponified", "elucidated", "gave", "given", "afforded", "resides", "residing", "associated", "separated", "generated", "revealed", "characterised", "provided", "cultivated"]

ACTION = ["resulted in", "led to", "lead to", "enabled the"]
PREP = ["from", "in", "by", "of"]
CONJUCTION = ["together", "along", "including"]
ABBR_TO_BE_REMOVED = ["sp", "syn", "var", "spp", "cf", "st", "No", "resp"]
ACTIVITY_AGAINST = ["activity", "activities", "active"]
N_MICRO_SAME_SENT = ["Coculture", "coculture", "Cocultures", "cocultures"]
N_ORG_SAME_SENT_CONJUNCTION = ["While", "while", "respectively"]


def get_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, micro_higher_rel):

    comp_org_rel_list = ", ".join(comp_micro_rel)
    comp_org_rel_dict = {
        "comp": comp_dict[0]["name"],
        "org": micro_org_dict[0]["name"],
        # "higher_org": higher_org_dict[0]["name"],
        "rel": comp_org_rel_list
    }

    if comp_org_rel_dict:
        return comp_org_rel_dict


def get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel):

    if comp_micro_rel:
        comp_org_rel_list = ", ".join(comp_micro_rel)
        comp_org_rel_dict = {
            "comp": comp_dict[0]["name"],
            "org": micro_org_dict[0]["name"],
            "rel": comp_org_rel_list
        }

        if comp_org_rel_dict:
            return comp_org_rel_dict

    elif comp_higher_rel:
        comp_org_rel_list = ", ".join(comp_higher_rel)
        comp_org_rel_dict = {
            "comp": comp_dict[0]["name"],
            "org": higher_org_dict[0]["name"],
            "rel": comp_org_rel_list
        }

        if comp_org_rel_dict:
            return comp_org_rel_dict


def get_n_org_n_comp_same_sent_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, case):

    comp_org_rel_list = []

    if comp_micro_rel:

        for org in micro_org_dict:
            if org["label"] in comp_micro_rel: 
                comp_org_rel_list.append(org["name"])

        if case == "coculture_micro_rel_same_sent":
            comp_org_rel_dict = {
                "comp": comp_dict[0]["name"],
                "org": ", ".join(comp_org_rel_list),
                "rel": "cocultures"
            }
        
        elif case == "all_micro_rel_same_sent":
            comp_org_rel_dict = {
                "comp": comp_dict[0]["name"],
                "org": ", ".join(comp_org_rel_list),
                "rel": "multiple micro organisms in same sentence"
            }

        if comp_org_rel_dict:
            return comp_org_rel_dict
    
    elif comp_higher_rel:

        return []

    else:
        return []


def comp_rel_org_activities_result(abstract, comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, case):

    micro_org_pattern = "(micro_org_\d+)"
    higher_org_pattern = "(higher_org_\d+)"

    if case == "comp_rel_org_activities_org" or case == "comp_activities_org_rel_org":

        if comp_micro_rel:

            micro_org = re.findall(micro_org_pattern, abstract)[0]

            for org in micro_org_dict:
                if org["label"] == micro_org:
                    comp_org_rel_list = ", ".join(comp_micro_rel)
                    comp_org_rel_dict = {
                        "comp": comp_dict[0]["name"],
                        "org": org["name"],
                        "rel": comp_org_rel_list
                    }
                    return comp_org_rel_dict
        
        elif comp_higher_rel:

            higher_org = re.findall(higher_org_pattern, abstract)[0]
            # print("higher_org: ", higher_org)

            for org in higher_org_dict:
                if org["label"] == higher_org:
                    comp_org_rel_list = ", ".join(comp_higher_rel)
                    comp_org_rel_dict = {
                        "comp": comp_dict[0]["name"],
                        "org": org["name"],
                        "rel": comp_org_rel_list
                    }
                    return comp_org_rel_dict
                

# Return a dictionary of compounds for the current sentence/abstract
def get_comp_dict(abstract, doc, chem_list_item):

    # Count the number of compunds in the current abstract
    # Create a dictionary of length comp_n
    comp_pattern = "(comp_\d+)"
    comp_n = len(re.findall(comp_pattern, abstract))
    comp_dict = [dict() for x in range(comp_n)]

    for index in range(len(comp_dict)):
        comp_dict[index] = {
            "label": "",
            "name": "",
            "ancestor": []  # Can be used for dependency tree
        }

    # Loop through all the compounds in the current abstract
    # Add the compounds with a placeholder comp_# to comp_dict
    count = 0
    for token in doc:
        match = re.search("(comp_\d+)", token.text)
        if match:
            comp_dict[count]["label"] = token.text
            comp_dict[count]["name"] = chem_list_item[0]
            t_ancestors = token.ancestors
            for t_a in t_ancestors:
                comp_dict[count]["ancestor"].append(t_a)
            count = count + 1

    # print("comp_dict: ", comp_dict)
    return comp_dict


# Return a dictionary of micro organisms for the current sentence/abstract
def get_micro_org_dict(abstract, doc, source_list):
    
    # Count the number of micro organisms in the current abstract
    # Create a dictionary of length micro_org_n
    micro_org_match_list = re.findall(r"micro_org_\d+", abstract)
    micro_org_n = len(micro_org_match_list)
    micro_org_dict = [dict() for x in range(micro_org_n)]

    for index in range(len(micro_org_dict)):
        micro_org_dict[index] = {
            "label": "",
            "name": "",
            "ancestor": []  # Can be used for dependency tree
        }

    # Loop through all the organisms in the current abstract
    # Add the organisms with a placeholder micro_org_# to higher_org_dict
    for source in source_list:
        # print("source: ", source)
        if source["placeholder"] in micro_org_match_list:
            # print("source: ", source["text"])
            micro_org_dict[index]["label"] = source["placeholder"]
            micro_org_dict[index]["name"] = source["text"]

    # print("micro_dict: ", micro_org_dict)
    return micro_org_dict


# Return a dictionary of higher organisms for the current sentence/abstract
def get_higher_org_dict(abstract, doc, source_list):
    
    # Count the number of higher organisms in the current abstract
    # Create a dictionary of length higher_org_n
    higher_org_match_list = re.findall(r"higher_org_\d+", abstract)
    higher_org_n = len(higher_org_match_list)
    higher_org_dict = [dict() for x in range(higher_org_n)]

    for index in range(len(higher_org_dict)):
        higher_org_dict[index] = {
            "label": "",
            "name": "",
            "ancestor": []  # Can be used for dependency tree
        }

    # Loop through all the organisms in the current abstract
    # Add the organisms with a placeholder higher_org_# to higher_org_dict
    index = 0
    for source in source_list:
        if source["placeholder"] in higher_org_match_list:
            higher_org_dict[index]["label"] = source["placeholder"]
            higher_org_dict[index]["name"] = source["text"]

    # print("higher_dict: ", higher_org_dict)
    return higher_org_dict


def get_one_org_n_comp_diff_sent_relation(abstract, doc, chem_list_item, source_list):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    # If comp > 0 and micro_org = 1 and higher_org = 0
    if comp_dict and micro_org_dict and not higher_org_dict:
        comp_org_rel_dict = {
            "comp": comp_dict[0]["name"],
            "org": micro_org_dict[0]["name"],
            "rel": "cross sentence"
        }
        if comp_org_rel_dict:
            return comp_org_rel_dict

    # If comp > 0 and micro_org = 0 and higher_org = 1
    elif comp_dict and not micro_org_dict and higher_org_dict:
        comp_org_rel_dict = {
            "comp": comp_dict[0]["name"],
            "org": higher_org_dict[0]["name"],
            "rel": "cross sentence"
        }   
        if comp_org_rel_dict:
            return comp_org_rel_dict

    # ???
    elif comp_dict:
        comp_org_rel_dict = {
            "comp": comp_dict[0]["name"],
            "org": micro_org_dict[0]["name"],
            "rel": "cross sentence"
        }
        if comp_org_rel_dict:
            return comp_org_rel_dict


def get_obtained_by_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "obtained_by_micro":

        pattern = re.compile(r"comp_\d+.*micro_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.search(substring)
            if pattern_rel_res:
                comp_micro_rel.append(pattern_rel_res.group(0))
                # print(pattern_res.group(0))
    else:
        pattern = re.compile(r"comp_\d+.*higher_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.search(substring)
            if pattern_rel_res:
                comp_higher_rel.append(pattern_rel_res.group(0))

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)




def get_of_org_rel_comp(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []
    
    if case == "of_micro_rel_comp":
        pattern = re.compile(r"micro_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)
    else:
        pattern = re.compile(r"higher_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_obtained_by_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel =[]

    if case == "obtained_by_micro":

        pattern = re.compile(r"comp_\d+.*micro_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.search(substring)
            if pattern_rel_res:
                comp_micro_rel.append(pattern_rel_res.group(0))
                # print(pattern_res.group(0))
    else:
        pattern = re.compile(r"comp_\d+.*higher_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.search(substring)
            if pattern_rel_res:
                comp_higher_rel.append(pattern_rel_res.group(0))

    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_of_org_rel_comp(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []
    
    if case == "of_micro_rel_comp":
        pattern = re.compile(r"micro_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)
    else:
        pattern = re.compile(r"higher_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_resulted_in_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "micro_resulted_in":
        pattern = re.compile(r"micro_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)
            else:
                pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(ACTION))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_micro_rel = pattern_rel_res
            
        else:
            pattern = re.compile(r'\b(%s)\b.*of.*comp_\d+.*micro_org_\d+' % '|'.join(RELATION4))
            pattern_res = pattern.search(abstract)
            if pattern_res:
                substring = pattern_res.group(0)
                # print("substring: ", substring)

                pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_micro_rel = pattern_rel_res

    else:
        pattern = re.compile(r"higher_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)
            else:
                pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(ACTION))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_higher_rel = pattern_rel_res
            
        else:
            pattern = re.compile(r'\b(%s)\b.*of.*comp_\d+.*higher_org_\d+' % '|'.join(RELATION4))
            pattern_res = pattern.search(abstract)
            if pattern_res:
                substring = pattern_res.group(0)
                # print("substring: ", substring)

                pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_higher_rel = pattern_rel_res        
    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_comp_rel_org_together_comp_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "comp_rel_micro_together_comp":
        pattern = re.compile(r'\b(%s)\b.*micro_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)
                
                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_micro_rel:
                    comp_micro_rel.remove("identified")

    else:
        pattern = re.compile(r'\b(%s)\b.*higher_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)
                
                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_higher_rel:
                    comp_higher_rel.remove("identified")
    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_comp_rel_together_comp_org_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "comp_rel_together_comp_micro":
        pattern = re.compile(r'\b(%s)\b.*\b(%s)\b.*comp_\d+.*micro_org_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)

                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_micro_rel:
                    comp_micro_rel.remove("identified")
    
    else:
        pattern = re.compile(r'\b(%s)\b.*\b(%s)\b.*comp_\d+.*higher_org_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)

                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_higher_rel:
                    comp_higher_rel.remove("identified")

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_rel_from_org_comp_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []
    
    if case == "rel_of_micro_comp":
        pattern = re.compile(r"\b(%s)\b.*from.*micro_org_\d+.*comp_\d+" % "|".join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            
            pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            # print(pattern_rel_res)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
    else:
        pattern = re.compile(r"\b(%s)\b.*from.*higher_org_\d+.*comp_\d+" % "|".join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            
            pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            # print(pattern_rel_res)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_of_comp_from_org_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "of_comp_from_micro":
        pattern = re.compile(r"\b(%s)\b.*of.*comp_\d+" % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(pattern_rel_res)
    else:
        pattern = re.compile(r"\b(%s)\b.*of.*comp_\d+" % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION4))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(pattern_rel_res)

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_comp_rel_org_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "comp_rel_micro":
        pattern = re.compile(r"comp_\d+.*micro_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            # print(pattern_rel_res)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(comp_micro_rel)

                # 70987
                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_micro_rel:
                    comp_micro_rel.remove("identified")

            if not comp_micro_rel:
                pattern = re.compile(r"\b(%s)\b.*comp_\d+.*micro_org_\d+" % "|".join(RELATION3))
                pattern_res = pattern.search(abstract)
                if pattern_res:
                    substring = pattern_res.group(0)
                    
                    pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
                    pattern_rel_res = pattern_rel.findall(substring)
                    # print(pattern_rel_res)
                    if pattern_rel_res:
                        comp_micro_rel = pattern_rel_res

    else:
        pattern = re.compile(r"comp_\d+.*higher_org_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
            pattern_rel_res = pattern_rel.findall(substring)
            # print(pattern_rel_res)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
                # print(comp_micro_rel)
                
                pattern_identified_as = re.compile(r"identified as")
                pattern_identified_as_res = pattern_identified_as.search(abstract)
                # print(pattern_identified_as_res)
                if pattern_identified_as_res and "identified" in comp_higher_rel:
                    comp_higher_rel.remove("identified")

            if not comp_higher_rel:
                pattern = re.compile(r"\b(%s)\b.*comp_\d+.*higher_org_\d+" % "|".join(RELATION3))
                pattern_res = pattern.search(abstract)
                if pattern_res:
                    substring = pattern_res.group(0)
                    
                    pattern_rel = re.compile(r"\b(%s)\b" % "|".join(RELATION3))
                    pattern_rel_res = pattern_rel.findall(substring)
                    # print(pattern_rel_res)
                    if pattern_rel_res:
                        comp_higher_rel = pattern_rel_res

    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_comp_was_rel_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    pattern = re.compile(r".*comp_\d+")
    pattern_res = pattern.search(abstract)
    # print(pattern_res)
    if pattern_res:
        start = pattern_res.end()
        substring = abstract[start:]
        # print("substring: ", substring)
        
        pattern_rel = re.compile(r'\b(%s)\b' % '|'.join(RELATION3))
        pattern_rel_res = pattern_rel.findall(substring)
        if pattern_rel_res:
            # print(pattern_rel_res)
            if case == "micro_comp_was_rel":
                comp_micro_rel = pattern_rel_res
            else:
                comp_higher_rel = pattern_rel_res
    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)
    

def get_org_rel_comp_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    if case == "micro_rel_comp":
        pattern = re.compile(r"micro_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)
            # print("micro_org_dict: ", micro_org_dict)

            pattern_rel = re.compile(r'\b(%s|%s|%s)\b' % ('|'.join(RELATION1), '|'.join(RELATION3), '|'.join(RELATION2)))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res
                # print(comp_micro_rel)
    else:
        pattern = re.compile(r"higher_org_\d+.*comp_\d+")
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s|%s|%s)\b' % ('|'.join(RELATION1), '|'.join(RELATION3), '|'.join(RELATION2)))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_higher_rel = pattern_rel_res
    
    return get_one_org_n_comp_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, micro_higher_rel)


def get_all_org_rel_same_sent_relation(abstract, doc, chem_list_item, source_list, case):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    comp_higher_rel = []

    if case == "coculture_micro_rel_same_sent" or case == "all_micro_rel_same_sent":

        pattern_rel = re.compile(r'micro_org_\d+')
        pattern_rel_res = pattern_rel.findall(abstract)
        if pattern_rel_res:
            # print(pattern_rel_res)
            comp_micro_rel = pattern_rel_res
            # match sourcelist and pattern_res based on placeholder

    # else:
    #     pattern_rel = re.compile(r'higher_org_\d+')
    #     pattern_rel_res = pattern_rel.findall(abstract)
    #     if pattern_rel_res:
    #         # print(pattern_rel_res)
    #         comp_higher_rel = pattern_rel_res

    return get_n_org_n_comp_same_sent_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, case)


def get_comp_rel_org_activities_relation(abstract, doc, chem_list_item, source_list, case):

    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    substring = ""
    comp_micro_rel = []
    comp_higher_rel = []
    micro_higher_rel = []

    # print("higher_org_dict: ", higher_org_dict)

    if case == "comp_rel_org_activities_org":
        pattern = re.compile(r'comp_\d+.*\b(%s)\b.*micro_org_\d+.*\b(%s)\b' % ('|'.join(RELATION3), '|'.join(ACTIVITY_AGAINST)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            # print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % ('|'.join(RELATION3)))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res

        else:
            pattern = re.compile(r'comp_\d+.*\b(%s)\b.*higher_org_\d+.*\b(%s)\b' % ('|'.join(RELATION3), '|'.join(ACTIVITY_AGAINST)))
            pattern_res = pattern.search(abstract)
            if pattern_res:
                substring = pattern_res.group(0)
                # print("substring: ", substring)

                pattern_rel = re.compile(r'\b(%s)\b' % ('|'.join(RELATION3)))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_higher_rel = pattern_rel_res

    elif case == "comp_activities_org_rel_org":
        # comp_\d+.*\b(%s)\b.*org_\d+.*\b(%s)\b.*micro_org_\d+
        pattern = re.compile(r'\b(%s)\b.*micro_org_\d+' % ('|'.join(RELATION3)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            substring = pattern_res.group(0)
            print("substring: ", substring)

            pattern_rel = re.compile(r'\b(%s)\b' % ('|'.join(RELATION3)))
            pattern_rel_res = pattern_rel.findall(substring)
            if pattern_rel_res:
                comp_micro_rel = pattern_rel_res

        else:
            pattern = re.compile(r'\b(%s)\b.*higher_org_\d+' % ('|'.join(RELATION3)))
            pattern_res = pattern.search(abstract)
            if pattern_res:
                substring = pattern_res.group(0)
                # print("substring: ", substring)

                pattern_rel = re.compile(r'\b(%s)\b' % ('|'.join(RELATION3)))
                pattern_rel_res = pattern_rel.findall(substring)
                if pattern_rel_res:
                    comp_higher_rel = pattern_rel_res
                
    return comp_rel_org_activities_result(substring, comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, comp_higher_rel, case)


def get_micro_higher_rel_comp_relation(abstract, doc, chem_list_item, source_list):
    comp_dict = get_comp_dict(abstract, doc, chem_list_item)
    micro_org_dict = get_micro_org_dict(abstract, doc, source_list)
    higher_org_dict = get_higher_org_dict(abstract, doc, source_list)

    comp_micro_rel = []
    micro_higher_rel = []
    # print("abstract: ", abstract)

    pattern = re.compile(r"micro_org_\d+.*higher_org_\d+")
    pattern_res = pattern.search(abstract)
    if pattern_res:
        start = pattern_res.end()
        substring = abstract[start:]
        # print("substring: ", substring)

        pattern_rel = re.compile(r'\b(%s|%s|%s)\b' % ('|'.join(RELATION1), '|'.join(RELATION3), '|'.join(RELATION2)))
        pattern_rel_res = pattern_rel.findall(substring)
        if pattern_rel_res:
            comp_micro_rel = pattern_rel_res
            # print(comp_micro_rel)
    
    return get_result(comp_dict, micro_org_dict, higher_org_dict, comp_micro_rel, micro_higher_rel)


def determine_n_org_same_sent_case(abstract, rel):

    pattern = re.compile(r'\b(%s)\b' % ('|'.join(N_MICRO_SAME_SENT)))
    pattern_res = pattern.search(abstract)
    if pattern_res:
        return "coculture_micro_rel_same_sent"

    pattern = re.compile(r'\b(%s|%s)\b' % ('|'.join(ACTIVITY_AGAINST), '|'.join(N_ORG_SAME_SENT_CONJUNCTION)))
    pattern_res = pattern.search(abstract)
    if not pattern_res:
        if rel == "n_micro_no_higher_n_comp_same_sent":
            return "all_micro_rel_same_sent"
        
        # This was returning None
        # else:
        #     return "all_higher_rel_same_sent"


def determine_rel_activities_same_sent_case(abstract):
    
    # comp_1 (1), comp_5, isolated from the seeds and bark of higher_org_1, were tested for insect antifeedant and growth regulatory activities against the tobacco cutworm, higher_org_2
    pattern = re.compile(r'comp_\d+.*\b(%s)\b.*org_\d+.*\b(%s)\b.*org_\d+' % ('|'.join(RELATION3), '|'.join(ACTIVITY_AGAINST)))
    pattern_res = pattern.search(abstract)
    if pattern_res:
        # print("comp rel higher_org1 [activities, against] higher_org2")
        return "comp_rel_org_activities_org"

    # comp_\d+.*\b(%s)\b.*org_\d+.*\b(%s)\b.*micro_org_\d+.*obtained from.*higher_org_\d+
    pattern = re.compile(r'comp_\d+.*\b(%s)\b.*org_\d+.*\b(%s)\b.*org_\d+' % ('|'.join(ACTIVITY_AGAINST), '|'.join(RELATION3)))
    pattern_res = pattern.search(abstract)
    if pattern_res:
        # print("comp rel higher_org1 [activities, against] higher_org2")
        return "comp_activities_org_rel_org"


def determine_case(abstract, rel):

    # If micro = 1 and (higher = 0 or higher = 1)
    if rel == "one_micro_no_higher_n_comp_same_sent":

        pattern = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "obtained_by_micro"

        pattern = re.compile(r'\b(%s)\b.*of.*micro_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION4), '|'.join(RELATION3)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "of_micro_rel_comp"

        pattern = re.compile(r'\b(%s)\b.*comp_\d+' % '|'.join(ACTION))
        # pattern = re.compile(r'resulted in.*comp_\d+')
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "micro_resulted_in"

        pattern = re.compile(r'\b(%s)\b.*micro_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_micro_together_comp"

        pattern = re.compile(r'\b(%s)\b.*\b(%s)\b.*comp_\d+.*micro_org_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_together_comp_micro"

        pattern = re.compile(r'\b(%s)\b.*from.*micro_org_\d+.*comp_\d+' % '|'.join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "rel_from_micro_comp"

        pattern = re.compile(r'\b(%s)\b.*of.*comp_\d+.*from.*micro_org_\d+' % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "of_comp_from_micro"

        pattern = re.compile(r'comp_\d+.*\b(%s)\b.*micro_org_\d+' % '|'.join(RELATION3))
        # pattern = re.compile(r'comp_\d+.*\b(%s)\b.*micro_org_\d+' % '|'.join(PREP))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_micro"

        pattern = re.compile(r'.*micro_org_\d+.*comp_\d+.*\b(%s)\b' % '|'.join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "micro_comp_was_rel"
   
        pattern = re.compile(r'.*micro_org_\d+(?!.*\bhigher_org_\d+\b).*\b(%s|%s|%s)\b.*comp_\d+' % ('|'.join(RELATION1), '|'.join(RELATION3), '|'.join(RELATION2)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "micro_rel_comp"

    # If micro = 0 and higher = 1
    elif rel == "no_micro_one_higher_n_comp_same_sent":

        pattern = re.compile(r'obtained by.*\b(%s)\b' % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "obtained_by_higher"

        pattern = re.compile(r'\b(%s)\b.*of.*higher_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION4), '|'.join(RELATION3)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "of_higher_rel_comp"

        pattern = re.compile(r'\b(%s)\b.*comp_\d+' % '|'.join(ACTION))
        # pattern = re.compile(r'resulted in.*comp_\d+')
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "higher_resulted_in"

        pattern = re.compile(r'\b(%s)\b.*higher_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_higher_together_comp"

        pattern = re.compile(r'\b(%s)\b.*\b(%s)\b.*comp_\d+.*higher_org_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_together_comp_higher"

        pattern = re.compile(r'\b(%s)\b.*higher_org_\d+.*\b(%s)\b.*comp_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_higher_together_comp"

        pattern = re.compile(r'\b(%s)\b.*\b(%s)\b.*comp_\d+.*higher_org_\d+' % ('|'.join(RELATION3), '|'.join(CONJUCTION)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_together_comp_higher"

        pattern = re.compile(r'\b(%s)\b.*from.*higher_org_\d+.*comp_\d+' % '|'.join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "rel_from_higher_comp"

        pattern = re.compile(r'\b(%s)\b.*of.*comp_\d+.*from.*higher_org_\d+' % '|'.join(RELATION4))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "of_comp_from_higher"

        pattern = re.compile(r'comp_\d+.*\b(%s)\b.*higher_org_\d+' % '|'.join(RELATION3))
        # pattern = re.compile(r'comp_\d+.*\b(%s)\b.*higher_org_\d+' % '|'.join(PREP))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "comp_rel_higher"

        pattern = re.compile(r'.*higher_org_\d+.*comp_\d+.*\b(%s)\b' % '|'.join(RELATION3))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "higher_comp_was_rel"        

        pattern = re.compile(r'.*higher_org_\d+(?!.*\bmicro_org_\d+\b).*\b(%s|%s|%s)\b.*comp_\d+' % ('|'.join(RELATION1), '|'.join(RELATION3), '|'.join(RELATION2)))
        pattern_res = pattern.search(abstract)
        if pattern_res:
            # print(pattern_res.group())
            return "higher_rel_comp"

    elif rel == "one_micro_one_higher_n_comp_same_sent":
        return determine_rel_activities_same_sent_case(abstract)
    
    elif rel == "one_org_n_comp_diff_sent":
        return "one_org_n_comp_diff_sent"
    
    elif rel == "one_micro_one_higher_n_comp_diff_sent":
        return "one_micro_one_higher_n_comp_diff_sent"
        
    elif rel == "n_micro_no_higher_n_comp_same_sent":
        return determine_n_org_same_sent_case(abstract, rel)
    
    elif rel == "no_micro_n_higher_n_comp_same_sent":
        return determine_rel_activities_same_sent_case(abstract)
    
    elif rel == "n_micro_n_higher_n_comp_same_sent":
        return determine_rel_activities_same_sent_case(abstract)


def remove_words_from_abstract(compound_tuple):
    # print("compound_tuple ", compound_tuple)
    to_be_removed_pattern = re.compile(r'\b(%s)\b[.]' % '|'.join(ABBR_TO_BE_REMOVED))
    # print(to_be_removed)
    sub_text = re.sub(pattern=to_be_removed_pattern, string=compound_tuple[2], repl='')
    sent_text = nltk.sent_tokenize(sub_text)
    
    return sent_text


def call_corresponding_relation_function(abstract, doc, item, source_list, case):

    if case == "obtained_by_micro" or case == "obtained_by_higher":
        return get_obtained_by_relation(abstract, doc, item, source_list, case)
        
    elif case == "of_micro_rel_comp" or case == "of_higher_rel_comp":
        return get_of_org_rel_comp(abstract, doc, item, source_list, case)

    elif case == "micro_resulted_in" or case == "higher_resulted_in":
        return get_resulted_in_relation(abstract, doc, item, source_list, case)

    elif case == "comp_rel_micro_together_comp" or case == "comp_rel_higher_together_comp":
        return get_comp_rel_org_together_comp_relation(abstract, doc, item, source_list, case)
        
    elif case == "comp_rel_together_comp_micro" or case == "comp_rel_together_comp_higher":
        return get_comp_rel_together_comp_org_relation(abstract, doc, item, source_list, case)

    elif case == "rel_from_micro_comp" or case == "rel_from_higher_comp":
        return get_rel_from_org_comp_relation(abstract, doc, item, source_list, case)

    elif case == "of_comp_from_micro" or case == "of_comp_from_higher":
        return get_of_comp_from_org_relation(abstract, doc, item, source_list, case)
        
    elif case == "comp_rel_micro" or case == "comp_rel_higher":
        return get_comp_rel_org_relation(abstract, doc, item, source_list, case)

    elif case == "micro_comp_was_rel" or case == "higher_comp_was_rel":
        return get_comp_was_rel_relation(abstract, doc, item, source_list, case)

    elif case == "micro_rel_comp" or case == "higher_rel_comp":
        return get_org_rel_comp_relation(abstract, doc, item, source_list, case)

    elif case == "micro_higher_rel_comp":
        return get_micro_higher_rel_comp_relation(abstract, doc, item, source_list)

    elif case == "one_org_n_comp_diff_sent":
        result = get_one_org_n_comp_diff_sent_relation(abstract, doc, item, source_list)
        if result:
            return result

    elif case == "one_micro_one_higher_n_comp_diff_sent":
        result = get_one_org_n_comp_diff_sent_relation(abstract, doc, item, source_list)
        if result:
            return result

    elif case == "all_micro_rel_same_sent":
        return get_all_org_rel_same_sent_relation(abstract, doc, item, source_list, case)
    
    elif case == "coculture_micro_rel_same_sent":
        return get_all_org_rel_same_sent_relation(abstract, doc, item, source_list, case)

    elif case == "comp_rel_org_activities_org" or case == "comp_activities_org_rel_org":
        return get_comp_rel_org_activities_relation(abstract, doc, item, source_list, case)


def get_relation(chem_list, source_list, original_abstract):

    if isinstance(original_abstract, str) and chem_list and not source_list: 
        return []
    
    elif isinstance(original_abstract, str) and not chem_list and source_list:
        return []
    
    elif isinstance(original_abstract, str) and chem_list and source_list:

        list_for_dict = []

        micro_org_pattern = "(micro_org_\d+)"
        higher_org_pattern = "(higher_org_\d+)"
        comp_pattern = "(comp_\d+)"

        # print("original_abstract: ", abstract, "\n")
        original_micro_org_abstract_n = len(re.findall(micro_org_pattern, original_abstract))
        original_higher_org_abstract_n = len(re.findall(higher_org_pattern, original_abstract))

        # If there's org > 3 in the abstract
        if original_micro_org_abstract_n + original_higher_org_abstract_n > 3:

            ignored_pattern = re.compile(r'\b(%s)\b' % '|'.join(ACTIVITY_AGAINST))

            for item in chem_list:
                temp_abstract = ""

                sent_text = nltk.sent_tokenize(item[2])
                for sent in sent_text:
                    ignored_pattern_res = ignored_pattern.search(sent)
                    if ignored_pattern_res:
                        micro_res = re.findall(micro_org_pattern, sent)
                        higher_res = re.findall(higher_org_pattern, sent)
                        if micro_res or higher_res:
                            continue
                        else:
                            temp_abstract = temp_abstract + sent
                    else:
                        temp_abstract = temp_abstract + sent
                item = tuple(temp_abstract if x == item[2] else x for x in item)

                # print(item)
                new_abstract = temp_abstract
            # print("new_abstract: ", abstract)

        else:
            new_abstract = original_abstract
    
        micro_org_abstract_n = len(re.findall(micro_org_pattern, new_abstract))
        higher_org_abstract_n = len(re.findall(higher_org_pattern, new_abstract))

        if (micro_org_abstract_n + higher_org_abstract_n == 1) or (micro_org_abstract_n == 1 and higher_org_abstract_n == 1):
            
            for item in chem_list:

                rel = ""
                sent_text = remove_words_from_abstract(item)

                for sent in sent_text:
                
                    abstract = sent
                    # print("abstract_sent: ", abstract)
                    doc = nlp(abstract)

                    micro_org_sent_n = len(re.findall(micro_org_pattern, abstract))
                    higher_org_sent_n = len(re.findall(higher_org_pattern, abstract))
                    comp_n = len(re.findall(comp_pattern, abstract))

                    # print("abstract: ", abstract)
                    if comp_n > 0 and (micro_org_sent_n + higher_org_sent_n > 0):

                        if micro_org_sent_n == 1 and higher_org_sent_n == 0:
                            rel = "one_micro_no_higher_n_comp_same_sent"

                        elif micro_org_sent_n == 0 and higher_org_sent_n == 1:
                             rel = "no_micro_one_higher_n_comp_same_sent"
                        
                        elif micro_org_sent_n == 1 and higher_org_sent_n == 1: 
                            rel = "one_micro_one_higher_n_comp_same_sent"

                    else:

                        if comp_n == 0 and (micro_org_sent_n + higher_org_sent_n > 0) or comp_n > 0 and (micro_org_sent_n + higher_org_sent_n == 0):

                            if micro_org_abstract_n + higher_org_abstract_n == 1:
                                # rel = "one_org_n_comp_diff_sent"
                                continue
                            
                            elif micro_org_abstract_n == 1 and higher_org_abstract_n == 1: 
                                # print(sent)
                                # rel = "one_micro_one_higher_n_comp_diff_sent"
                                continue
                        
                            else:
                                continue

                        else:
                            continue

                    # print("rel: ", rel)
                    case = determine_case(abstract, rel)
                    # print("org = 1 case: ", case)
                    rel_to_be_added = call_corresponding_relation_function(abstract, doc, item, source_list, case)
                    if rel_to_be_added:
                        list_for_dict.append(rel_to_be_added)

        else:

            for item in chem_list:
                
                rel = ""
                sent_text = remove_words_from_abstract(item)

                for sent in sent_text:

                    abstract = sent
                    # print("abstract_sent: ", abstract)
                    doc = nlp(abstract)
                    
                    micro_org_sent_n = len(re.findall(micro_org_pattern, abstract))
                    higher_org_sent_n = len(re.findall(higher_org_pattern, abstract))
                    comp_n = len(re.findall(comp_pattern, abstract))
                    # print("micro_org_n: ", micro_org_n, " comp_n: ", comp_n)

                    if comp_n > 0 and (micro_org_sent_n + higher_org_sent_n > 0):

                        if micro_org_sent_n == 1 and higher_org_sent_n == 0:
                            rel = "one_micro_no_higher_n_comp_same_sent"

                        elif micro_org_sent_n == 0 and higher_org_sent_n == 1:
                             rel = "no_micro_one_higher_n_comp_same_sent"
                        
                        elif micro_org_sent_n == 1 and higher_org_sent_n == 1: 
                            rel = "one_micro_one_higher_n_comp_same_sent"
                        
                        elif micro_org_sent_n > 1 and higher_org_sent_n == 0: 
                            # rel = "n_micro_no_higher_n_comp_same_sent"
                            continue
                        
                        elif micro_org_sent_n == 0 and higher_org_sent_n > 1: 
                            # rel = "no_micro_n_higher_n_comp_same_sent"
                            continue

                        else:
                            # rel = "n_micro_n_higher_n_comp_same_sent"
                            continue

                    else:
                        # rel = "n_org_diff_sent"
                        continue

                    # print("rel: ", rel)
                    case = determine_case(abstract, rel)
                    # print("case: ", case)
                    
                    rel_to_be_added = call_corresponding_relation_function(abstract, doc, item, source_list, case)
                    if rel_to_be_added:
                        list_for_dict.append(rel_to_be_added)
                    
        if list_for_dict:
            return list_for_dict

        else:
            return []
    else:
        return []
