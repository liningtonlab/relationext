## NER-RE Pipeline Scripts:

- [main.py](main.py)
- [compound_name_extractor.py](compound_name_extractor.py)
- [organism_categorizer.py](organism_categorizer.py) Takes the Taxonerd results as input, checks if the species of an organism entity exists in `microbial_genera_list`, `plant_genera_list`, `animal_genera_list`, or `pathogen_genera_list`. Labels the organism entity as a **micro_org_#** if it is in the microbial_genera_list, **higher_org_#** if in the plant_genera_list or animal_genera_list, and **pathogen_org_#** if in the pathogen_genera_list. Replaces the organism entity in the abstract with its corresponding placeholder.
- [relation_extractor.py](relation_extractor.py)