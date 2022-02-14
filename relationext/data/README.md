# Required Data

## For compound entities:
1. [npatlas_root_name_list.xlsx](npatlas_root_name_list.xlsx) An excel file containing a list of microbial compounds and their corresponding root names in the NP-Atlas for capturing compound entities in journal abstracts. Microbial compounds and their root names can be directly edited, added, or removed from this excel file.

2. [npuatlas_root_name_list.xlsx](npuatlas_root_name_list.xlsx) An excel file containing a list of plant compounds and their corresponding root names in the Universal Atlas for capturing compound entities in journal abstracts. Plant compounds and their root names can be directly edited, added, or removed from this excel file.

3. [marine_root_name_list.xlsx](marine_root_name_list.xlsx) An excel file containing a list of marine compounds and their corresponding root names for capturing compound entities in journal abstracts. Marine compounds and their root names can be directly edited, added, or removed from this excel file.

4. [npatlas_root_name_list.txt](npatlas_root_name_list.txt) A text file generated from the corresponding excel file `npatlas_root_name_list.xlsx` containing a list of microbial compound root names from compounds in the NP-Atlas for capturing compound entities in journal abstracts. Used in `./src/root_name_extractor.py`. **_Do not_** directly edit, add, or remove root names from this text file.

5. [npuatlas_root_name_list.txt](npuatlas_root_name_list.txt) A text file generated from the corresponding excel file `npuatlas_root_name_list.xlsx` containing a list of plant compound root names from compounds in the  Universal Atlas for capturing compound entities in journal abstracts. Used in `./src/root_name_extractor.py`. **_Do not_** directly edit, add, or remove root names from this text file.

6. [marine_root_name_list.txt](marine_root_name_list.txt) A text file generated from the corresponding excel file `marine_root_name_list.xlsx` containing a list of marine compound root names from compounds for capturing compound entities in journal abstracts. Used in `./src/root_name_extractor.py`. **_Do not_** directly edit, add, or remove root names from this text file.

7. [root_name_list.txt](root_name_list.txt) A text file containing all the microbial, plant, and marine compound root names from `npatlas_root_name_list.txt`, `npuatlas_root_name_list.txt`, and `marine_root_name_list.txt` and sorts them alphabetically for capturing compound entities in journal abstracts. Used in `./src/compound_name_extractor.py`. **_Do not_** directly edit, add, or remove root names from this text file. If a root names needs to be added or removed, do it through the above excel files.

8. [ignore_list.txt](ignore_list.txt) A text file containing a list of excluded terms for creating new compound root names and capturing compound entities in journal abstracts. Terms can be directly edited, added, or removed from this list. If a new terms needs to be excluded when creating root names or capturing compound entities, add it to this list. Used in `./src/source_organism_ner.py`, `./src/root_name_extractor.py`, and `./src/update_root_name_list.py`.

## For organism entities:

1. [microbe_genera_list.txt](microbe_genera_list.txt) A text file containing a list of microbial species that checks if an organism from Taxonerd's output is a microbial species and labels the organism as **micro_org_#**. Used in `./src/organism_categorization.py`. Mircrobial species can be directly edited, added, or removed from this list.

2. [plant_genera_list.txt](plant_genera_list.txt) A text file containing a list of plant species that checks if an organism from Taxonerd's output is a plant species and labels the organism as **higher_org_#**. Used in `./src/organism_categorization.py`. Plant species can be directly edited, added, or removed from this list.

3. [animal_genera_list.txt](animal_genera_list.txt) A text file containing a list of animal species that checks if an organism from Taxonerd's output is an animal species and labels the organism as **higher_org_#**. Used in `./src/organism_categorization.py`. Animal species can be directly edited, added, or removed from this list.

4. [pathogen_genera_list.txt](pathogen_genera_list.txt) A text file containing a list of common pathogens that checks if an organism from Taxonerd's output is a pathogen and labels the organism as **pathogen_org_#**. Used in `./src/organism_categorization.py`. Pathogens can be directly edited, added, or removed from this list.