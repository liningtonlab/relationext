import re
import sys
import pandas as pd

def test_matching_compound(data_df):
    """Performs an Accuracy & Coverage test between automated NER-RE result and manual annotated result on compounds only.
        :param data_df: dataframe that contains named columns: compound_by_ner, compound_by_root, unique_relation, annotated_compound, and annotated_relation
        :return: None
        """

    total = len(data_df)
    number_of_comp = 0
    number_of_manual_comp = 0
    whole_data_ner_matching_manual = 0
    whole_data_number_of_manual_matched = 0

    for index, row in data_df.iterrows():

        try:

            rel_num = 0
            comp_by_ner_list =  row["compound_by_ner"].split("), (")
            comp_by_root_list = row["compound_by_root"].split("), (")
            ner_unique_comp_list = []

            man_rel_num = 0
            man_compound_list = row["annotated_compound"].split("; ")
            man_comp_list = []

            # print(row["index"], "-----------------------------")

            for comp in comp_by_ner_list:
                match = re.finditer(r"\'(.*)\'\,\s\(", comp)
                for m in match:
                    # print(m.group(1))
                    # print("\n")
                    ner_unique_comp_list.append(m.group(1))
            
            for comp in comp_by_root_list:
                match = re.finditer(r"\'(.*)\'\,\s\(", comp)
                for m in match:
                    # print(m.group(1))
                    ner_unique_comp_list.append(m.group(1))
            
            ner_unique_comp_list = list(set(ner_unique_comp_list))
            print(ner_unique_comp_list)
                
            if "[]" in man_compound_list:
                man_compound_list.remove("[]")

            if len(ner_unique_comp_list) == 0 and len(man_compound_list) == 0:
                total = total - 1
                print("No compound in both data set\n")
                continue

            if len(ner_unique_comp_list) > 0:    
                for rel in ner_unique_comp_list:
                    
                    rel_num = rel_num + 1
                    # print(rel_num)
                    relation_dict_list = [{}]*rel_num
                    for el in range(len(relation_dict_list)):
                        relation_dict_list[el] = {
                            "comp": "",
                            "flag": 0
                        }

                for el in range(len(relation_dict_list)):
                    relation_dict_list[el]["comp"] = ner_unique_comp_list[el]

            man_rel_num = len(man_compound_list)
            man_relation_dict_list = [{}]*man_rel_num
            for el in range(len(man_relation_dict_list)):
                man_relation_dict_list[el] = {
                    "comp": "",
                    "flag": 0
            }
            if man_rel_num > 0:    
                for rel in man_compound_list:
                    
                    # print(man_rel_num)
                    man_comp_list.append(rel)

                for el in range(len(man_relation_dict_list)):
                    man_relation_dict_list[el]["comp"] = man_comp_list[el]
            
            number_of_ner_matching_manual = 0
            for man in range(len(man_relation_dict_list)):
                for ner in range(len(relation_dict_list)):
                    if relation_dict_list[ner]["comp"].lower() == man_relation_dict_list[man]["comp"].lower():
                        number_of_ner_matching_manual = number_of_ner_matching_manual + 1
                        relation_dict_list[ner]["flag"] = 1
            
            if number_of_ner_matching_manual > 0:
                whole_data_ner_matching_manual = whole_data_ner_matching_manual + number_of_ner_matching_manual
                print("number_of_ner_matching_annotated: %i/%i" % (number_of_ner_matching_manual, len(ner_unique_comp_list)), " ", round(number_of_ner_matching_manual/len(ner_unique_comp_list)*100, 1), "%")
                for ner in range(len(relation_dict_list)):
                    if relation_dict_list[ner]["flag"] != 1:
                        print(relation_dict_list[ner])
            else:
                print("number_of_ner_matching_annotated: %i/%i" % (number_of_ner_matching_manual, len(ner_unique_comp_list)), " 0%")

            number_of_comp = number_of_comp + len(ner_unique_comp_list)


            number_of_manual_matched = 0
            for ner in range(len(relation_dict_list)):
                for man in range(len(man_relation_dict_list)):
                    if relation_dict_list[ner]["comp"].lower() == man_relation_dict_list[man]["comp"].lower():
                        number_of_manual_matched = number_of_manual_matched + 1
                        man_relation_dict_list[man]["flag"] = 1

            if number_of_manual_matched > 0:
                whole_data_number_of_manual_matched = whole_data_number_of_manual_matched + number_of_manual_matched
                print("\nnumber_of_annotated_matched_by_ner: %i/%i" % (number_of_manual_matched, len(man_compound_list)), " ", round(number_of_manual_matched/len(man_compound_list)*100, 1), "%")
            else:
                print("\nnumber_of_annotated_matched_by_ner: %i/%i" % (number_of_manual_matched, len(man_compound_list)), " 0%")
            
            for man in range(len(man_relation_dict_list)):
                if man_relation_dict_list[man]["flag"] != 1:
                    print(man_relation_dict_list[man])
            
            number_of_manual_comp = number_of_manual_comp + len(man_compound_list)

            print("\n")
        
        except IndexError as e:
            print(e)

    print("Accuracy: %i/%i  %0.1f" % (whole_data_ner_matching_manual, number_of_comp, (whole_data_ner_matching_manual/number_of_comp)*100) + "%")
    print("Coverage: %i/%i  %0.1f" % (whole_data_number_of_manual_matched, number_of_manual_comp, (whole_data_number_of_manual_matched/number_of_manual_comp)*100) + "%")


def test_matching_relation(data_df):
    """Performs an Accuracy & Coverage test between automated NER-RE result and manual annotated result on relationships {comp, org, rel}.
        :param data_df: dataframe that contains named columns: compound_by_ner, compound_by_root, unique_relation, annotated_compound, and annotated_relation
        :return: None
        """

    total = len(data_df)
    number_of_comp = 0
    number_of_manual_comp = 0
    whole_data_ner_matching_manual = 0
    whole_data_number_of_manual_matched = 0
    ner_rel_not_matching_list = []

    for index, row in data_df.iterrows():

        try:

            rel_num = 0
            ner_relation_list = row["unique_relation"].split("},")
            # print(ner_relation_list)

            ner_comp_list = []
            ner_org_list = []
            ner_rel_list = []

            man_rel_num = 0
            man_relation_list = row["annotated_relation"].split("},")
            man_comp_list = []
            man_org_list = []
            man_rel_list = []

            # print(row["index"], "-----------------------------")

            for rel in ner_relation_list:

                rel_num = rel_num + 1
                rel = rel.replace('"', "'")
                comp_pattern = re.finditer(r"comp\'\:\s\'(.*)\'\,\s\'org", rel)
                for text in comp_pattern:
                    # print(text[1])
                    ner_comp_list.append(text[1])

                org_pattern = re.finditer(r"org\'\:\s\'(.*)\'\,\s\'rel", rel)
                for text in org_pattern:
                    # print(text[1])
                    ner_org_list.append(text[1])
                
                rel_pattern = re.finditer(r"rel\'\:\s\'(.*)\'", rel)
                for text in rel_pattern:
                    # print(text[1])
                    ner_rel_list.append(text[1])

            relation_dict_list = [{}]*rel_num
            for el in range(len(relation_dict_list)):
                relation_dict_list[el] = {
                    "comp": "",
                    "org": "",
                    "rel": "",
                    "flag": 0
                }

            print(relation_dict_list)
            
            for el in range(len(relation_dict_list)):
                relation_dict_list[el]["comp"] = ner_comp_list[el]
                relation_dict_list[el]["org"] = ner_org_list[el]
                relation_dict_list[el]["rel"] = ner_rel_list[el]

            if "[]" in man_relation_list:
                man_relation_list.remove("[]")

            if len(ner_comp_list) == 0 and len(man_comp_list) == 0:
                total = total - 1
                print("No compound in both data set\n")
                continue

            # print(man_relation_list)
            for rel in man_relation_list:
                # print("rel: ", rel)
                man_rel_num =  man_rel_num + 1
                rel = rel.replace('"', "'")
                comp_pattern = re.finditer(r"comp\'\:\s\'(.*)\'\,\s\'org", rel)
                for text in comp_pattern:
                    # print(text[1])
                    man_comp_list.append(text[1])

                org_pattern = re.finditer(r"org\'\:\s\'(.*)\'\,\s\'rel", rel)
                for text in org_pattern:
                    # print(text[1])
                    man_org_list.append(text[1])
                
                rel_pattern = re.finditer(r"rel\'\:\s\'(.*)\'", rel)
                for text in rel_pattern:
                    # print(text[1])
                    man_rel_list.append(text[1])
                
            # print(man_rel_num)
            man_relation_dict_list = [{}]*man_rel_num
            for el in range(len(man_relation_dict_list)):
                man_relation_dict_list[el] = {
                    "comp": "",
                    "org": "",
                    "rel": "",
                    "flag": 0
                }

            # print(len(man_comp_list), len(man_org_list), len(man_rel_list))
            for el in range(len(man_relation_dict_list)):
                man_relation_dict_list[el]["comp"] = man_comp_list[el]
                man_relation_dict_list[el]["org"] = man_org_list[el]
                man_relation_dict_list[el]["rel"] = man_rel_list[el]

            
            number_of_correct_ner = 0
            for man in range(len(man_relation_dict_list)):
                for ner in range(len(relation_dict_list)):
                    if relation_dict_list[ner]["comp"] == man_relation_dict_list[man]["comp"] and relation_dict_list[ner]["org"].lower() == man_relation_dict_list[man]["org"].lower() and relation_dict_list[ner]["rel"].lower() == man_relation_dict_list[man]["rel"].lower():
                        number_of_correct_ner = number_of_correct_ner + 1
                        relation_dict_list[ner]["flag"] = 1
                        break
            
            for ner in range(len(relation_dict_list)):
                if relation_dict_list[ner]["flag"] == 0:
                    ner_rel_not_matching_list.append(relation_dict_list[ner]["rel"])
            
            if number_of_correct_ner > 0:
                whole_data_ner_matching_manual = whole_data_ner_matching_manual + number_of_correct_ner
                print("number_of_ner_matching_annotated: %i/%i" % (number_of_correct_ner, len(ner_relation_list)), " ", round(number_of_correct_ner/len(ner_relation_list)*100, 1), "%")
            else:
                print("number_of_ner_matching_annotated: %i/%i" % (number_of_correct_ner, len(ner_relation_list)), " 0%")
                
            for ner in range(len(relation_dict_list)):
                    if relation_dict_list[ner]["flag"] != 1:
                        print(relation_dict_list[ner])

            number_of_comp = number_of_comp + len(ner_relation_list)
            # print("number_of_correct_ner: ", whole_data_ner_matching_manual)
            # print("number_of_cumulative_relation: ", number_of_comp)

            number_of_man_getting_matched = 0
            for ner in range(len(relation_dict_list)):
                for man in range(len(man_relation_dict_list)):
                    if relation_dict_list[ner]["comp"] == man_relation_dict_list[man]["comp"] and relation_dict_list[ner]["org"].lower() == man_relation_dict_list[man]["org"].lower() and relation_dict_list[ner]["rel"].lower() == man_relation_dict_list[man]["rel"].lower():
                        number_of_man_getting_matched = number_of_man_getting_matched + 1
                        man_relation_dict_list[man]["flag"] = 1
                        break
            
            if number_of_man_getting_matched > 0:
                whole_data_number_of_manual_matched = whole_data_number_of_manual_matched + number_of_man_getting_matched
                print("\nnumber_of_annotated_matched_by_ner: %i/%i" % (number_of_man_getting_matched, len(man_relation_list)), " ", round(number_of_man_getting_matched/len(man_relation_list)*100, 1), "%")
            else:
                print("\nnumber_of_annotated_matched_by_ner: %i/%i" % (number_of_man_getting_matched, len(man_relation_list)), " 0%")
            
            for man in range(len(man_relation_dict_list)):
                if man_relation_dict_list[man]["flag"] != 1:
                    print(man_relation_dict_list[man])
            
            number_of_manual_comp = number_of_manual_comp + len(man_relation_list)
            print("\n")
        
        except IndexError as e:
            print(e)

    print("Accuracy: %i/%i  %0.1f" % (whole_data_ner_matching_manual, number_of_comp, (whole_data_ner_matching_manual/number_of_comp)*100) + "%")
    print("Coverage: %i/%i  %0.1f" % (whole_data_number_of_manual_matched, number_of_manual_comp, (whole_data_number_of_manual_matched/number_of_manual_comp)*100) + "%")
    # print(ner_rel_not_matching_list)


def main():
    """Performs an Accuracy & Coverage test between automated NER-RE result and manual annotated result on compounds only or on relationships {comp, org, rel}.
        :param sys.argv[1]: input excel filename, do not need to specify file extension, 
                            must contain named columns: compound_by_ner, compound_by_root, unique_relation, annotated_compound, and annotated_relation
        :param sys.argv[2]: flag -0 or -1 indicating which variable to perform the test on
        :return: None
        """
    try:

        print("filepath: ", "../trained_result/" + sys.argv[1] + ".xlsx")
        assert len(sys.argv) == 3
        
        data_df = pd.read_excel("../trained_result/" + sys.argv[1] + ".xlsx", index_col=None)
        
        # Performs Accuracy & Coverage for compounds only.
        if sys.argv[2] == "-0":
            test_matching_compound(data_df)
        
        # Performs Accuracy & Coverage for relationships {comp, org, rel}.
        elif sys.argv[2] == "-1":
            test_matching_relation(data_df)

        else:
            print("Invalid arguments. Please enter a valid filename and flag.\n")

    except AssertionError as e1:
        print("Invalid arguments. Please enter a valid filename and flag.\n", e1)
    except OSError as e2:
        print("Invalid arguments. Please enter a valid filename and flag.\n", e2)


if __name__ == "__main__":
    main()
