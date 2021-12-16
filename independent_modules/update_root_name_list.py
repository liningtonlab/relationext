import sys
import pandas as pd

def update_individual_textfile_with_excel(root_name_df, filename):
    
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

# This is a stand-alone program and is not part of the NER-RE pipeline.
# This program updates the 
def main():
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