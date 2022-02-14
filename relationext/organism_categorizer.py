import pandas as pd
import pkg_resources as pkr


# Reads a text file and appends the items in the text file to a list.
def read_text_file(filename):
    with open(filename) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        # print(lines)
        return lines


# Organism lists used in match_org(user).
micro_list = read_text_file(pkr.resource_string(__name__, "microbe_genera_list.txt"))
plant_list = read_text_file("data/plant_genera_list.txt")
animal_list = read_text_file("data/animal_genera_list.txt")
pathogen_list = read_text_file("data/pathogen_genera_list.txt")


def match_org(user):
    """Checks if the species of an organism entity exists in microbial_genera_list, plant_genera_list, animal_genera_list, or pathogen_genera_list
        and assigns it a label.
        :param user: name of the organism entity
        :return: string indicating the type of organism entity
        """
    
    if any(xs in user for xs in pathogen_list):
        match = user
        # print(match)
        if match:
            return 'pathogen_org'

    elif any(xs in user for xs in micro_list):
        match = user
        # print(match)
        if match:
            return 'micro_org'
    
    elif any(xs in user for xs in plant_list):
        match = user
        # print(match)
        if match:
            return 'higher_org'
    
    elif any(xs in user for xs in animal_list):
        match = user
        # print(match)
        if match:
            return 'higher_org'
    else:
        return None


def taxonerd_list_to_df(org_list):
    """Converts Taxonerd list into dataframe. Result will be passed to get_placeholder_for_org().
        :param org_list: list containing Taxonerd result
        :return: dataframe containing Taxonerd result
        """
    data = []
    source_df = pd.DataFrame()

    if org_list:
        for item in org_list:
            # print(item)
            offsets = item.get("offsets")
            splits = offsets.split()
            start = int(splits[1])
            end = int(splits[2])
            temp_dict = {
                "start": start, 
                "end": end, 
                "text": item.get("text")
                }
                    
            data.append(
                temp_dict
            )
            # print(data)
            source_df = pd.DataFrame(data, columns=['start', 'end', 'text'])
            source_df['type'] = source_df['text'].apply(match_org)   # find the micro matches
            # print(source_df)

    return source_df


def get_placeholder_for_org(org_df):
    """Assigns a numbered placeholder to each organism entity returned by Taxonerd.
            :param org_df: dataframe containing Taxonerd result
            :return: dataframe containing Taxonerd result with a new column called placeholder
            """

    n_micro = 0
    n_higher = 0
    placeholder = []

    for index, row in org_df.iterrows():
        if row['type'] == "micro_org":
             n_micro = n_micro + 1
             placeholder.append("micro_org_" + str(n_micro))
        elif row['type'] == "higher_org":
            n_higher = n_higher + 1
            placeholder.append("higher_org_" + str(n_higher))
        else:
            placeholder.append(None)

    org_df["placeholder"] = placeholder
    # print(placeholder)
    return org_df
    

def taxonerd_df_to_dict(org_list):
    """Converts Taxonerd dataframe into dictionary. The result will be passed to ./relation_extractor.py.
                :param org_list: list of Taxonerd result
                :return: list of dictionaries
                """

    if org_list:
        # print(org_list)
        org_df = taxonerd_list_to_df(org_list)
        mod_org_df = get_placeholder_for_org(org_df)
        
        mod_org_dict = mod_org_df.to_dict('records')
        # print(mod_org_dict)
        return mod_org_dict
    else:
        return []


def replace_org_in_abstract(abstract, org_list):
    """Replaces the micro organisms and higher organisms in the abstract with a placeholder and returns the new abstract to ./main.py.
                    :param abstract: raw string of abstract text
                    :param org_list: list of Taxonerd result
                    :return: a string of new abstract text
                    """

    if isinstance(abstract, str) and isinstance(org_list, list):
        new_abstract = ""

        try:
            org_df = taxonerd_list_to_df(org_list)
            mod_org_df = get_placeholder_for_org(org_df)

            prev_end = 0

            n_micro = 0
            n_higher = 0
            abstract_len = len(abstract)
            # print("abstract_len: ", abstract_len)

            for index, row in mod_org_df.iterrows():
                # print(row['start'], row['end'], row['text'], row['type'])

                new_abstract = new_abstract + abstract[prev_end:row['start']]

                if row['type'] == "micro_org":
                    n_micro = n_micro + 1
                    new_abstract = new_abstract + row['placeholder']

                elif row['type'] == "higher_org":
                    n_higher = n_higher + 1
                    new_abstract = new_abstract + row['placeholder']

                else:
                    new_abstract = new_abstract + row['text']
                
                if row['end'] != abstract_len:
                    new_abstract = new_abstract + abstract[row['end']]
                else:
                    new_abstract = new_abstract + "."
                
                prev_end = row['end'] + 1
                # print(n_micro, " ", n_higher)

            new_abstract = new_abstract + abstract[prev_end:]

        except IndexError as e:
            print(e)
            # print(new_abstract)
            
        return new_abstract        