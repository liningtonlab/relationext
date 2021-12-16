#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd 


# In[3]:


npatlas_compound = pd.read_excel("/Volumes/Seagate Backup Plus Drive/SFU/Coop/2021_Summer/contextual_extraction/ner_ml_0907/NPAtlas_download.xlsx", index_col=None)


# In[56]:


data = pd.read_excel("/Volumes/Seagate Backup Plus Drive/SFU/Coop/2021_Summer/contextual_extraction/ner_ml_0907/ml_1_ner_0_org_1_comp_0_micro.xlsx", index_col=None)


# In[8]:


npatlas_compound_list = npatlas_compound['compound_names'].tolist()


# In[58]:


# sub = npatlas_compound.loc[0:5]
data.head(5)


# In[37]:


npatlas_compound_list


# In[57]:


matching_compound_list = [[]] * len(data)
len(matching_compound_list)


# In[ ]:


count = 0
for index, row in data.iterrows():
    print(count)
    res = [comp for comp in npatlas_compound_list if(comp in row["abstract"])]
    if (bool(res) == True):
        print(res)
        matching_compound_list[count] = res
    count = count + 1


# In[53]:


matching_compound_list


# In[54]:


info = {"matching_compound": matching_compound_list}
info_df = pd.DataFrame(data=info)
data_merged = data.join(info_df)
data_merged


# In[ ]:




