import re
import sys
import json
import time
import pandas as pd

t = time.time()

def load_data(filename, compound_column_name):

    compound_df = pd.read_excel(filename, index_col=None)

    # Store your DataFrame
    # compound_df.to_pickle('cached_compound_raw.pkl') # will be stored in current directory

    # Read your DataFrame
    # compound_df = pd.read_pickle(filename) # read from current directory
    compound_df = compound_df[[compound_column_name]] # TODO: make user specify compound column name from terminal?s
    compound_df = compound_df.dropna() 

    # compound_df = compound_df[["npaid", "compound_names"]].sort_values(by = ["compound_names"])
    # compound_df = compound_df[compound_df["compound_names"] != "Not named"]
    compound_df = compound_df[compound_df[compound_column_name].map(len) > 5]
    compound_df = compound_df[compound_df[compound_column_name].map(len) < 25]
    compound_df = compound_df[compound_df[compound_column_name].str.contains(r"\d{5,}", regex=True) == False]
    # compound_df = compound_df.iloc[205:215]

    # print(compound_df)
    return compound_df


# Extract the root name from compounds that contain only alphabets.
def match_alpha_only(raw_compound, ignore_list, leading_names):
    compound_name_match = re.finditer(r"^[a-zA-Z]+$", raw_compound)
    for comp in compound_name_match:
        if comp not in ignore_list+leading_names:
            return comp[0]


# Extract the root name from compounds that are followed by a letter, eg. Examplamides A.
def match_name_with_variant(raw_compound, ignore_list, leading_names):
    compound_name_match = re.finditer(r"^[a-zA-Z]+\s(?!acid)[a-zA-Z\d+\-]{1,5}$", raw_compound)
    for comp in compound_name_match:
        split_list = re.split(r"\s", comp[0])
        if split_list[0] not in ignore_list+leading_names:
            return split_list[0]


# Extract the root name from compounds that have the term "acid" as part of the full compound name.
def match_acid_name(raw_compound, ignore_list, leading_names):

    # Compound acid
    compound_name_match = re.findall(r"(?:\w+\s|\w+\'){0,3}\w+\s\bacid\b", raw_compound)

    if compound_name_match:
        for comp in compound_name_match:
            # print("comp: ", comp)
            acid_name = comp.split(" ")
            # print("acid_name: ", acid_name)
            
            for item in acid_name:
                if not item.isalpha():
                    acid_name.remove(item)

            if acid_name[0].lower() not in ignore_list+leading_names:
                return " ".join(acid_name)
            else:
                return "acid_no_root"


# Extract the root name from compounds that are none of the above.
def match_complex_name(raw_compound, ignore_list, leading_names):
    split_list = re.split(r"\W", raw_compound)
    # print(raw_compound, split_list, len(split_list))
    
    item_list = []
    for item in split_list:
        if item.isalpha() and len(item) > 5 and len(item) < 25 and item.lower() not in ignore_list+leading_names:
            item_list.append(item)
    
    if len(item_list) > 1:
        for item in item_list:
            if item.lower() in ignore_list+leading_names or re.search(r"\d+", item):
                item_list.remove(item)
    
    # print(item_list)
    if len(item_list) == 1:
        return item_list[0]

    elif len(item_list) > 1:
        return max(item_list, key=len)    # TODO: this needs to handle when a compound has more than 1 root name
    

# Determines the type of compound and calls the corresponding function.
def match_root_name(raw_compound, ignore_list, leading_names_list):
    """When the root name for a compound cannot be automatically extracted, it requires manual extraction from user.
        :param raw_compound: compound to extract the root name from
        :param ignore_list: a list of terms that should be ignored when extracting the root names int an abstract
        :param leading_names_list: a list of prefixes that should be ignored when extracting the root names int an abstract
        :return: extracted root name
        """

    # print(raw_compound)
    root_name = ""

    root_name = match_acid_name(raw_compound, ignore_list, leading_names_list)
    
    if root_name:
        if root_name != "acid_no_root":
            # print("3")
            return root_name.capitalize()
    else:

        root_name = match_alpha_only(raw_compound, ignore_list, leading_names_list)
        if root_name and root_name not in ignore_list+leading_names_list:
            # print("1")
            return root_name.capitalize()
        
        root_name = match_name_with_variant(raw_compound, ignore_list, leading_names_list)
        if root_name and root_name not in ignore_list+leading_names_list:
            # print("2")
            return root_name.capitalize()

        root_name = match_complex_name(raw_compound, ignore_list, leading_names_list)
        if root_name and root_name not in ignore_list+leading_names_list:
            # print("4")
            return root_name.capitalize()
    

# After extracting the root name from a compound, remove the leading terms in the root name.
def remove_leading_name(comp, leading_names_list):
    """When the root name for a compound cannot be automatically extracted, it requires manual extraction from user.
        :param root_matched_df: dataframe with 2 columns, one containing compound names and one containing corrsponding root name
        :param compound_column_name: the column that contains compound names
        :param ignore_list: a list of terms that should be ignored when detecting the root names int an abstract
        :return: a list of root names detected in the abstractr each compound
        """

    temp = ""
    removing_list = []

    if comp:
    
        for l in leading_names_list:
            if re.match(r"^%s" % l, comp):
                removing_list.append(l)
        
        if not removing_list:
            temp = comp.capitalize()
            return temp
        
        else:
            
            # print("removing_list: ", removing_list)
            removing_name = max(removing_list, key=len)
            
            # print("removing_name ", removing_name)
            compound_split = re.split(r"%s" % removing_name, comp)
        
            compound_split = [c.strip(" ") for c in compound_split]
            compound_split = [c for c in compound_split if c]
            # print("compound_split: ", compound_split)
            
            if len(compound_split) == 0:
                return None
            else:
                return remove_leading_name(" ".join(compound_split), leading_names_list)


def capitalize_root_matched(root_extracted):
    """Clean up and format the extracted root names by capitalzing it, remove the ones that have equal or fewer than 5 characters 
        and the ones that have "No_root" as the root.
        :param root_extracted: the extracted root name for a compound
        :return: cleaned and formatted root name
        """

    if root_extracted:
        if root_extracted == "No_root":
            return None
        elif root_extracted.isalpha() and len(root_extracted) > 5:
            return root_extracted.capitalize()
        elif len(root_extracted) < 6:
            return None
        else:
            return root_extracted


def get_root_name_list(root_matched_df, root_column_name, ignore_list):
    """When the root name for a compound cannot be automatically extracted, it requires manual extraction from user.
        :param root_matched_df: dataframe with 2 columns, one containing compound names and one containing corrsponding root name
        :param compound_column_name: the column that contains compound names
        :param ignore_list: a list of terms that should be ignored when detecting the root names int an abstract
        :return: a list of root names detected in the abstractr each compound
        """
    
    root_matched_df = root_matched_df.dropna()
    root_matched_df = root_matched_df[root_matched_df[root_column_name].map(len) > 5]
    root_matched_df = root_matched_df[root_matched_df[root_column_name].str.contains(r"\d+", regex=True) == False]
    root_matched_df = root_matched_df.drop_duplicates(subset = [root_column_name])
    root_name_list = root_matched_df[root_column_name].tolist()

    for root in root_name_list:
        if root.lower() in ignore_list:
            root_name_list.remove(root)

    return root_name_list


def extract_root_name_manually(compound_df, compound_column_name, root_name_list):
    """When the root name for a compound cannot be automatically extracted, it requires manual extraction from user.
        :param compound_df: dataframe with a column that contains compound names
        :param compound_column_name: the column that contains compound names
        :param root_name_list: a list of root names that were already detected in the abstract
        :return: a new dataframe with a column containing extracted root name for each compound
        """
    
    compound_df_copy = compound_df.copy(deep=True)

    assigned_root = [""]*len(compound_df_copy)
    ind = 0

    for index, row in compound_df_copy.iterrows():

        root_list_len = len(root_name_list)
        
        root_name_first_letter = [x[0] for x in root_name_list]
        root_name_after_first = [x[1:] for x in root_name_list]
        root_name_first_lower = [x.lower() for x in root_name_first_letter]

        flag = 0
        # print(ind, row[compound_column_name])

        if not row["root_name"] or row["root_name"] == "Skipped":
            count = 0
            while count < root_list_len:
                reg = root_name_first_letter[count] + root_name_after_first[count]
                reg_l = root_name_first_lower[count] + root_name_after_first[count]
                
                match_list = re.finditer("%s|%s" % (reg, reg_l), row[compound_column_name]) # TODO: make this compare lower to lower
                count = count + 1
        
                for match in match_list:
                    assigned_root[ind] = match[0]
                    # print("assigned_root[ind]: ", assigned_root[ind])
                    flag = 1
                    row["root_name"] = assigned_root[ind]
                    break
                else:
                    continue
            
            if flag == 0:
            
                user_input = input("Enter a a root name for [" + row[compound_column_name] + "] or choose from the following options:\n'c' to keep the full compound name as root name\n's' to skip the current compound\n'n' if compound has no root\n'e' to save and exit\n")
                if user_input == "c":
                    assigned_root[ind] = row[compound_column_name]
                    root_name_list.append(assigned_root[ind])
                    row["root_name"] = assigned_root[ind].capitalize()
                    
                elif user_input == "e":
                    compound_df["root_name"] = compound_df["root_name"].apply(capitalize_root_matched)
                    # compound_df_copy.to_excel("test_root_name_extractor_result.xlsx", index=False)
                    # compound_df_copy.to_excel("npuatlas_root_name_list_halfway.xlsx", index=False)
                    break
                elif user_input == "s":
                    row["root_name"] = "Skipped"
                elif user_input == "n":
                    row["root_name"] = "No_root"
                else:
                    assigned_root[ind] = user_input
                    # print("in else", user_input)
                    root_name_list.append(assigned_root[ind])
                    row["root_name"] = assigned_root[ind].capitalize()
                    # print(compound_df_copy)
        
        ind = ind + 1
    
    return compound_df_copy


# Removes pluralization on the root names.
def remove_pluralization(root):
    """Removes pluralization on the root names.
        :param root: root name of a compound
        :return: None
        """
    try:
        if root:
            if re.match(r".*ins$", root) or re.match(r".*es$", root) or re.match(r".*iods$", root):
                # print(root[:len(root)-1])
                return root[:len(root)-1]
            else:
                return root
    except TypeError as e:
        print("Error.", e)


def main():
    """Extracts root names from compound names.
        :param sys.argv[1]: input excel filename, do not need to specify file extension, must contain a columns of compounds names
        :param sys.argv[2]: name of the column that contains the compounds
        :param sys.argv[3]: output filename, do not need to specify file extension as it is automatically set to xlsx
        :return: None
        """
    try:
        assert len(sys.argv) == 4
        with open("../data/leading_names_to_ignore.txt") as file:
            lines = file.readlines()
            leading_names_list = [line.rstrip() for line in lines]
            leading_names_list = leading_names_list + [l.lower() for l in leading_names_list]
            # print(leading_names)
        file.close()

        with open("../data/ignore_list.txt") as file:
            lines = file.readlines()
            ignore_list = [line.rstrip() for line in lines]
            ignore_list = ignore_list + [x.lower() for x in ignore_list]
            # print(root_name_list)
        file.close()
        
        compound_df_raw = load_data("../data/" + sys.argv[1] + ".xlsx", sys.argv[2])
        # compound_df_copy = compound_df.copy(deep=True)

        compound_df_raw["root_name"] = compound_df_raw[sys.argv[2]].apply(match_root_name, ignore_list = ignore_list, leading_names_list = leading_names_list)
        compound_df_raw["root_name"] = compound_df_raw["root_name"].apply(remove_leading_name, leading_names_list = leading_names_list)
        # print(compound_df_raw)

        temp_name_list = get_root_name_list(compound_df_raw, "root_name", ignore_list)
        # print(len(temp_name_list))

        compound_df_clean = extract_root_name_manually(compound_df_raw, sys.argv[2], temp_name_list)
        # print(compound_df_clean)

        compound_df_clean["root_name"] = compound_df_clean["root_name"].apply(capitalize_root_matched)
        compound_df_clean["root_name"] = compound_df_clean["root_name"].apply(remove_pluralization)
        compound_df_clean = compound_df_clean.dropna()
        compound_df_clean = compound_df_clean.drop_duplicates(subset = ["root_name"])
        compound_df_clean = compound_df_clean[compound_df_clean["root_name"] != "No_root"]
        compound_df_clean = compound_df_clean[~compound_df_clean.root_name.isin([x.capitalize() for x in ignore_list+leading_names_list])]
        
        compound_df_clean.to_excel("../data/" + sys.argv[3] + ".xlsx", index=False)
        print('Elapsed: %.3f seconds' % (time.time() - t))

    except AssertionError:
        print("Invalid arguments. Please enter a valid filename and column name.\n")
    except OSError:
        print("Invalid arguments. Please enter a valid filename and column name.\n")


if __name__ == "__main__":
    main()
