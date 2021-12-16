# Trained Result

## 1M Pubmed Data

Parts of the data have to be downloaded from another [cloud drive](https://vault.sfu.ca/index.php/s/oKZ44IlZsKo2Btj) due to large file size.

1. [pubmed_priority_taxonerd_ner_1](https://vault.sfu.ca/index.php/s/h3Z5bbvp5nJTxCf) contains trained result from 1 million PubMed articles where NER_result = 1.
```bash
# The dataset is generated using this Mongo aggregated pipeline.
# Pipeline exported as Python 3:
[
    {
        '$match': {
            'NER_result': 1
        }
    }, {
        '$project': {
            '_id': 0, 
            'taxonerd': 1, 
            'taxonerd_title': 2, 
            'abstract': 3, 
            'doi': 4, 
            'pmid': 5, 
            'title': 6, 
            'NER_result': 7, 
            'organism': 8, 
            'compound_by_ner': 9, 
            'compound_by_root': 10, 
            'relation_by_ner': 11, 
            'relation_by_root': 12, 
            'relation_unique': 13, 
            'relation_title': 14, 
            'numberOfNer': {
                '$cond': {
                    'if': {
                        '$isArray': '$compound_by_ner'
                    }, 
                    'then': {
                        '$size': '$compound_by_ner'
                    }, 
                    'else': 'NA'
                }
            }, 
            'numberOfRoot': {
                '$cond': {
                    'if': {
                        '$isArray': '$compound_by_root'
                    }, 
                    'then': {
                        '$size': '$compound_by_root'
                    }, 
                    'else': 'NA'
                }
            }
        }
    }
]
```

2. [andrew_inner_join_pubmed_priority_taxonerd](https://vault.sfu.ca/index.php/s/omTayOcX4Muqw4w) contains Andrew's manual annotated dataset inner-joined with the 1 million PubMed articles on doi.
```bash
# The dataset is generated using this Mongo aggregated pipeline.
# Pipeline exported as Python 3:
[
    {
        '$lookup': {
            'from': 'articles', 
            'localField': 'doi', 
            'foreignField': 'doi', 
            'as': 'fromArticles'
        }
    }, {
        '$match': {
            'fromArticles': {
                '$ne': []
            }
        }
    }, {
        '$replaceRoot': {
            'newRoot': {
                '$mergeObjects': [
                    {
                        '$arrayElemAt': [
                            '$fromArticles', 0
                        ]
                    }, '$$ROOT'
                ]
            }
        }
    }, {
        '$project': {
            'fromArticles': 0
        }
    }
]
```

3. [pubmed_priority_taxonerd_comp_1](https://vault.sfu.ca/index.php/s/Huqe4bxT68HazWE) ccontains trained result from 1 million PubMed articles where an abstract has at least 1 compound.
```bash
# The dataset is generated using this Mongo aggregated pipeline.
# Query exported as Python 3:
{
 filter: {
  $or: [
   {
    'compound_by_ner.0': {
     $exists: true
    }
   },
   {
    'compound_by_root.0': {
     $exists: true
    }
   }
  ]
 }
}
```
4. [pubmed_priority_taxonerd_containing_matching_npatlas_comp](https://vault.sfu.ca/index.php/s/TvD9jSE93zb5TfI) contains trained result from 1 million PubMed articles where an abstract has at least 1 compound that is also in the NPAtlas.
```bash
# Module to generate this dataset:
cd independent_modules
$ 1m_pubmed_ner_re.py
```

5. [pubmed_priority_taxonerd_ner_1_matching_npatlas_comp](https://vault.sfu.ca/index.php/s/bleXMcDhE2kUrVS) contains trained result from 1 million PubMed articles where NER_result = 1 and the abstract also has at least 1 compound that is in the NPAtlas.
```bash
# Module to generate this dataset:
cd independent_modules
$ 1m_pubmed_ner_re.py
```

6. Other useful Mongo queries that I used to analyze the trained result:
```bash
# NER=0 & (Andrew new=1 | known=1 | both=1) & Taxonerd=0
{$and:[{NER_result:0}, {$or:[{New_NP_result:"1"}, {Known_NP_result:"1"}]}, {"taxonerd.0":{$exists:false}}]}
```
```bash
#  NER=0 & (Andrew new=1 | known=1 | both=1) & Taxonerd=0 & (comp_by_ner=1 or comp_by_ner=1)
{$and:[{NER_result:0}, {$or:[{New_NP_result:"1"}, {Known_NP_result:"1"}]}, {$and:[{"taxonerd.0":{$exists:false}}, {$or:[{"compound_by_ner.0":{$exists:true}}, {"compound_by_root.0":{$exists:true}}]}]}]}
```

## 100K Articles Data

1. [ner_ml_result_allroot_no_cross_sent](./100K_articles/ner_ml_result_allroot_no_cross_sent.xlsx) originally started with 100k articles, but left with 80k articles after removing duplicates and the ones with no doi. The arguments used are all the combined root names from microbes, plants, and marine, as well as no cross-sentence relationships.

2. [test_ner_ml_result_allroot_no_cross_sent](./100K_articles/test_ner_ml_result_allroot_no_cross_sent.xlsx) randomly selected 100 articles from `ner_ml_result_allroot_no_cross_sent.xlsx` and did manual curation to do an Accuracy & Coverage test between munual annotated result and NER-RE result.

3. [root_name_count](./100K_articles/root_name_count.xlsx) contains the number of times that a root name got matched in 80k abstracts.