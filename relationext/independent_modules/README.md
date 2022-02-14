## Stand-alone Scripts

Each module in this section is independent of each other with different functionalities for different purposes. 

1. [root_name_extractor.py](root_name_extractor.py) contains a column of compounds that the root names need to be extracted for. 
```bash
# Takes one input excel file, one column name, and one ouput filename as arguments. File extensions do not need to be specified as it is set to automatically import and export excel files.
$ root_name_extractor.py [INPUT_FILENAME] [COLUMN_NAME_FOR_COMPOUND] [OUTPUT_FILENAME]

$ root_name_extractor.py npatlas_root_name_list compound_name npatlas_root_name_list
$ root_name_extractor.py marine_root_name_list compound marine_root_name_list
```
2. [update_root_name_list.py](update_root_name_list.py) when a new root name is added to the excel files `npatlas_root_name_list.xlsx`, `npuatlas_root_name_list.xlsx`, and/or `marine_root_name_list.xlsx` or removed from it, use this script to also update the respective text files individually. Then, all three lists are automatically combined together into one unique list to update `./data/root_name_list.txt` with new result. 
```bash
# Takes at least one root name excel file as argument. File extension does not need to be specified as it is set to automatically import excel files. User can specify more than one root name excel file to be updated at once.
$ update_root_name_list.py [INPUT_FILENAME]

$ update_root_name_list.py npatlas_root_name_list
$ update_root_name_list.py npatlas_root_name_list marine_root_name_list.xlsx
```
3. [manual_annotation_test.py](manual_annotation_test.py) performs an Accuracy & Coverage test between automated trained data result and manual annoated result for the compounds and relationships.
```bash
# Takes an excel file from ./trained_result as argument. File extension does not need to be specified as it is set to automatically import excel files. The imported excel file must contain columns named: compound_by_ner, compound_by_root, unique_relation, annotated_compound, and annotated_relation.
$ manual_annotation_test [FILENAME] [OPTION]

Options:
    -0     Compare compounds only
    -1     Compare relationships {comp, org, rel}

$ manual_annotation_test test_ner_ml_result_allroot_no_cross_sent -1
```
4. [1m_pubmed_ner_re.py](1m_pubmed_ner_re.py) performs named entity recognition and relation extraction for 1 million PubMed articles via ijson.
```bash
$ 1m_pubmed_ner_re.py
```