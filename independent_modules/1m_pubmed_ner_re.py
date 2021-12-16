import re
import json
import ijson
import time
import gc
from enum import unique
from os import EX_SOFTWARE

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import src
from src import organism_categorizer,  compound_name_extractor, relation_extractor
# from organism_categorizer import taxonerd_df_to_dict, replace_org_in_abstract
# from compound_name_extractor import chem_ner_prototype, get_compound
# from relation_extractor import get_relation


# scan json file, run entry one at a time
# compute a bunch of output files, break them up into chunks
def combine_json_results():
    """Combines multiple json files into one single file and exports.
        :return: None
        """

    with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_result_" + "1" + ".json", "r") as file:
            data = json.load(file)
            # print(len(data))
            file.close()

    for i in range(2, 110):
        with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_result_" + str(i) + ".json", "r") as file:
            data2 = json.load(file)
            print(i, len(data2))
            file.close()

            for element in data2:
                data.append(element)

    with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_result.json", "w") as ner_result:
        print(len(data))
        json.dump(data, ner_result, indent = 4, sort_keys = False)


def ner_er_pipeline():
    """Runs the NER-RE pipeline over 1 million of PubMed articles about natural products since 1970. 
        Input is a json file of a list of dictionaries, where a dictionary contains trained result for an articles.
        Since the Taxonerd result has been run, the Taxonerd step is skipped and the value is fetched by value.get("taxonerd").
        Dump the result as a json file in chunks of 10,000 articles.
        :return: None
        """

    with open("../data/root_name_textfile.txt") as file:
        lines = file.readlines()
        root_name_list = [line.rstrip() for line in lines]
        root_name_list = root_name_list + [x.lower() for x in root_name_list]

    t = time.time()
    parser = ijson.parse(open("../trained_result/1M_pubmed_articles/debug_pubmed_priority_taxonerd.json", "r"))
    
    count = 0
    max_num = 0
    set_num = 0
    output = []

    for value in ijson.items(parser, 'item'):
        try:
            if max_num < 10000:
                print(count)
                
                value["NER_result"] = 0
                value["organism"] = []
                value["compound_by_ner"] = []
                value["compound_by_root"] = []
                value["relation_by_ner"] = []
                value["relation_by_root"] = []
                value["relation_unique"] = []
                value["relation_title"] = []

                # Extraction relationsnips in the journal abstract.
                proper_entity_list = value.get("taxonerd")
                source_list = taxonerd_df_to_dict(proper_entity_list)
                # print("source_list: ", source_list)

                new_abstract = replace_org_in_abstract(value.get("abstract"), proper_entity_list)
                # print("new_abstract: ", new_abstract)

                chem_list_by_ner = chem_ner_prototype(new_abstract)
                chem_list_by_root = get_compound(new_abstract, root_name_list)

                rel_by_ner = get_relation(chem_list_by_ner, source_list, new_abstract)
                rel_by_root = get_relation(chem_list_by_root, source_list, new_abstract)

                unique_res = [dict(t) for t in {tuple(d.items()) for d in rel_by_ner+rel_by_root}]

                # Extraction relationsnips in the journal title.
                taxonerd_title = value.get("taxonerd_title")
                source_list_title = taxonerd_df_to_dict(taxonerd_title)
                new_abstract_title = replace_org_in_abstract(value.get("abstract"), taxonerd_title)

                chem_list_by_ner_title = chem_ner_prototype(new_abstract_title)
                chem_list_by_root_title = get_compound(new_abstract_title, root_name_list)

                rel_by_ner_title = get_relation(chem_list_by_ner_title, source_list_title, new_abstract_title)
                rel_by_root_title = get_relation(chem_list_by_root_title, source_list_title, new_abstract_title)

                unique_res_title = [dict(t) for t in {tuple(d.items()) for d in rel_by_ner_title+rel_by_root_title}]


                if unique_res:
                    value["NER_result"] = 1

                if source_list:
                    value["organism"] = source_list
                
                if chem_list_by_ner:
                    value["compound_by_ner"] = chem_list_by_ner

                if chem_list_by_root:
                    value["compound_by_root"] = chem_list_by_root

                if rel_by_ner:
                    value["relation_by_ner"] = rel_by_ner
                
                if rel_by_root:
                    value["relation_by_root"] = rel_by_root
                
                if unique_res:
                    value["relation_unique"] = unique_res
                
                if unique_res_title:
                    value["relation_title"] = unique_res_title

                # print(value)
                output.append(value)
                count = count + 1
                max_num = max_num + 1
            
                if max_num + 1 == 10001:
                    set_num = set_num + 1
                    # print(output)
                    print("-------set_num", set_num)
                    with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_result_" + str(set_num) + ".json", "w") as ner_result:
                        json.dump(output, ner_result, indent = 4, sort_keys = False)
                    max_num = 0
                    output = []
                    gc.collect()
                    print('Elapsed: %.3f seconds' % (time.time() - t))
            
        except ijson.IncompleteJSONError as e:
            print(e)
            continue
        
    set_num = set_num + 1
    print("-------set_num", set_num)
    with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_result_" + str(set_num) + ".json", "w") as ner_result:
        json.dump(output, ner_result, indent = 4, sort_keys = False)
        
    print('Elapsed: %.3f seconds' % (time.time() - t))


def check_for_atlas_comp_in_abstract():
    """Checks how many extracted compounds have a match in the NPAtlas.
        :return: None
        """

    try:

        with open("../data/NPAtlas_compound_list_simplified.txt") as file:
            lines = file.readlines()
            simplified_compound_list = [line.rstrip() for line in lines]

        comp_1_json = ijson.parse(open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_ner_1.json", "r"))

        count = 0
        article_containing_atlas_comp = 0
        matching_atlas_comp = []
        article_containing_atlas_comp_list = []
        unique_matching_article = []

        for value in ijson.items(comp_1_json, 'item'):
            compound_by_ner = value.get("compound_by_ner")
            compound_by_root = value.get("compound_by_root")
            matching_temp = []
            print(count)
            count = count + 1
            if value.get("doi"):
                for i in compound_by_ner+compound_by_root:
                    if re.sub(r'\W+', '', i[0].upper()) in simplified_compound_list:
                        matching_temp.append(i[0])   
                        # print(i[0], value.get("doi"))
                        article_containing_atlas_comp_list.append(value)
                
                if matching_temp:
                    unique_matching_article.append(value.get("doi"))
                    article_containing_atlas_comp = article_containing_atlas_comp + 1
                    matching_atlas_comp = matching_atlas_comp + matching_temp

        print("total_matching_articles:", article_containing_atlas_comp, "unique_articles:", len(list(set(unique_matching_article))))
        print("total_unique_matching_atlas_compounds:", len(matching_atlas_comp), "unique_compounds:", len(list(set(matching_atlas_comp))))

        # with open('../trained_result/1M_pubmed_articles/1M_ner_1_matching_npatlas_comp.txt', 'w') as f:
        #     for item in matching_atlas_comp:
        #         f.write("%s\n" % item)

        # with open("../trained_result/1M_pubmed_articles/pubmed_priority_taxonerd_ner_1_matching_npatlas.json", "w") as mated_result:
        #     json.dump(article_containing_atlas_comp_list, mated_result, indent = 4, sort_keys = False)

    except ijson.IncompleteJSONError as e:
        print(e)


def main():
    try:
        check_for_atlas_comp_in_abstract()
        # with open("../trained_result/1M_pubmed_articles/1M_matching_npatlas_comp.txt") as file:
        #     lines = file.readlines()
        #     npuatlas = [line.rstrip() for line in lines]
        #     file.close()
        #     print(len(npuatlas))
    except OSError as e:
        print(e)

if __name__ == "__main__":
    main()