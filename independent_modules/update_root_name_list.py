import sys
import pandas as pd

def update_individual_textfile_with_excel(root_name_df, filename):
    """Automatically updates the txt files for (1)microbial, (2)plant, or (3)marine, depending on which one the user specifies in the command.
        :return: None
        """
    
    with open("./data/ignore_list.txt") as file:
        lines = file.readlines()
        ignore_list = [line.rstrip() for line in lines]
        ignore_list = ignore_list + [x.lower() for x in ignore_list]
        # print(ignore_list)

    print("old len() of: " + filename, len(root_name_df))  
    root_name_df = root_name_df[~root_name_df.root_name.isin([x.capitalize() for x in ignore_list])]
    print("new len() of: " + filename, len(root_name_df))  
    root_name_df.to_excel("./data/" + filename + ".xlsx", index=False)

    root_name_list = root_name_df["root_name"].tolist()
    with open("./data/" + filename + ".txt", "w") as f:
        for item in root_name_list:
            f.write("%s\n" % item)
    # print(len(marine_df))        


def update_root_name_list():
    """Automatically updates "root_name_list.txt" when either of (npatlas_root_name_list.txt")
        :return: None
        """

    print("...updating the main root_name_list")
    with open("./data/npatlas_root_name_list.txt") as file:
        lines = file.readlines()
        npatlas_list = [line.rstrip() for line in lines]
        print("len() of npatlas root name list: ", len(npatlas_list))

    with open("./data/npuatlas_root_name_list.txt") as file:
        lines = file.readlines()
        npuatlas_list = [line.rstrip() for line in lines]
        print("len() of npuatlas root name list: ", len(npuatlas_list))

    with open("./data/marine_root_name_list.txt") as file:
        lines = file.readlines()
        marine_list = [line.rstrip() for line in lines]
        print("len() of marine root name list: ", len(marine_list))

    root_name_all = (npatlas_list + npuatlas_list + marine_list)
    root_name_all = list(dict.fromkeys(root_name_all))
    root_name_all.sort()
    print("len() of root_name_all list: ", len(root_name_all))

    with open('./data/root_name_list.txt', 'w') as f:
        for item in root_name_all:
            f.write("%s\n" % item)


def main():
    """The root name list "root_name_list.txt" is used in the NER-RE pipeline, which is generated by combining the unique result from the <txt files> of (1)microbial, (2)plant, and (3)marine.
        The user modifies/adds/removes the root names in their <xlsx files> and uses this program to update the content in the <txt files> for those 4 root name lists. 

        !!!Only the <xlsx files> for (1)microbial, (2)plant, and (3)marine can be directly modified by the user, DO NOT make changes/add/remove in their <txt files>!!! 
        !!!The list (4)all can only be updated using this program, DO NOT manually make changes/add/remove root names in the <txt file> for (4)allm doing so will result in inconsistency!!!

        Step to update the root name lists:
        (1) When there's a new root name, add it to "npatlas_root_name_list.xlsx".
            When there's a root name that needs to be removed, remove it from "npatlas_root_name_list.xlsx".
            When a new term is added to the "ignored_list.txt", also run this program.
        (3) Run this program using the command "update_root_name_list.py [XLSX_FILENAME]".
        (4) This will automatically update the <txt file> that is associated with this <xlsx file> as well as update the <txt file> for (4)all.

        :return: None
        """
        
    try:
        assert len(sys.argv) >= 2
        for input in sys.argv[1:]:
            full_path = "./data/" + input + ".xlsx"
            print("input: ", input, full_path)
            root_name_df = pd.read_excel(full_path, index_col=None)
            update_individual_textfile_with_excel(root_name_df, input)
    except AssertionError:
        print("Invalid arguments. Please enter a valid root name filename:\n[npatlas_root_name_list | npuatlas_root_name_list | marine_root_name_list]\n")
    except OSError:
        print("Invalid arguments. Please enter a valid root name filename:\n[npatlas_root_name_list | npuatlas_root_name_list | marine_root_name_list]\n")
    else:
        update_root_name_list()
        print("There's no error. Finished updating.")

if __name__ == "__main__":
    main()