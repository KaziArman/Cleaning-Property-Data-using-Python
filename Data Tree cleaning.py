#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import string
import time
import pandas as pd
import numpy as np


# In[4]:


file = 'C93 raw data.xlsx' #CHECK THE FILE NAME
xl = pd.ExcelFile(file)
print(xl.sheet_names)


# In[5]:


df = xl.parse('Sheet1') #CHECK THE SHEET NAME
df.head(3)


# # DO NOT RUN UNDER CELL IF IT's MOBILE HOME

# In[6]:


#indexNames = df[(df['LIVING AREA'] >= 1)].index
# Delete these row indexes from dataFrame
#df.drop(indexNames , inplace=True)


#indexNames = df[(df['NO. COMMERCIAL UNITS'] > 1)].index
# Delete these row indexes from dataFrame
#df.drop(indexNames , inplace=True)

#indexNames = df[(df['NO. RESIDENTIAL UNITS'] > 1)].index
# Delete these row indexes from dataFrame
#df.drop(indexNames , inplace=True)

#indexNames = df[(df['NUMBER OF BUILDINGS'] > 1)].index
# Delete these row indexes from dataFrame
#df.drop(indexNames , inplace=True)


# In[7]:


len(df)


# # Removing Blank Mailing Address

# In[8]:


df.dropna(subset=['MAILING STREET ADDRESS'], inplace=True)

df.head()


# # Keyword Cleaning

# In[9]:


len(df)


# In[10]:


govt_df = pd.read_csv('Govt Data Cleaning.csv')
gov_name=govt_df['govt_owner_name'].tolist()
match_pattern = fr"\b(?:{'|'.join(gov_name)})\b"

df = df[~df['OWNER MAILING NAME'].str.contains(match_pattern,na = False, case = False)]

#df = df[~df['OWNER MAILING NAME'].str.lower().isin([x.lower() for x in gov_name])]


# with open('Govt Data Cleaning.txt',encoding='cp850', errors='replace') as fo:
#     f = fo.readlines()
#     l = len(f)
#     h=[]
#     h.clear()
#     a = ''
#     for w in range(l):
#         h.append(f[w])
#         a = "".join(h)
#         a = a.replace("\n","")
#         a = a.replace("''","")
#         #print(a)
#         p = a
#         #FOR DATA TREE
#         df = df[~df['OWNER MAILING NAME'].str.contains(a, na=False, case=False)]
#         #print(df)
#         a = ''
#         h.clear()
# 

# In[11]:


len(df)


# # Auto FIling Site Zip Code

# In[12]:


df["SITUS ZIP CODE"].count()


# In[13]:


df["SITUS ZIP CODE"] = df["SITUS ZIP CODE"].fillna(method='ffill')
df["SITUS ZIP CODE"].count()


# In[14]:


#df.to_excel('raw.xlsx')


# # Creating File for Address Verification

# In[15]:


df.insert(0,'SL no', range(1,1+len(df)))


# In[16]:


selected_columns = df[["SL no",
                       "OWNER MAILING NAME",
                       "MAILING STREET ADDRESS",
                        "MAIL CITY",
                        "MAIL STATE",
                        "MAIL ZIP/ZIP+4"]]
lob_df = selected_columns.copy()
lob_df = lob_df.rename(columns={"OWNER MAILING NAME" : "Name",
                                "MAILING STREET ADDRESS" : "Street", 
                                "MAIL CITY" : "City", 
                                "MAIL STATE" : "State", 
                                "MAIL ZIP/ZIP+4" : "ZIP"})


# In[17]:


lob_df


# In[18]:


lob_df.to_csv('AccuZip_in.csv',index = False)


# # Importing Output from AccuZip

# In[19]:


lob_out1 = pd.read_csv("AccuZip_out.csv")


# In[20]:


df.head(3)


# In[21]:


lob_out1.head(3)


# In[22]:


lob_out1 = lob_out1.rename(columns={"sl_no": "SL no",
                                  "first" : "OWNER MAILING NAME",
                                  "address" : "MAILING STREET ADDRESS",
                                  "city" : "MAIL CITY",
                                  "st" : "MAIL STATE",
                                  "zip" : "MAIL ZIP/ZIP+4",
                                  #"last_line" : "Full Address",
                                  "status_" : "Mailing Status"})
lob_out1


# In[23]:


selected_columns2 = lob_out1[["SL no",
                       "OWNER MAILING NAME",
                       "MAILING STREET ADDRESS",
                        "MAIL CITY",
                        "MAIL STATE",
                        "MAIL ZIP/ZIP+4",
                              #"Full Address",
                       "Mailing Status"]]
lob_out = selected_columns2.copy()
lob_out


# In[24]:


lob_out['Mailing Status'] = np.where(lob_out['Mailing Status'] =='V','Deliverable', lob_out['Mailing Status'])
lob_out['Mailing Status'] = np.where(lob_out['Mailing Status'] =='M','Undeliverable', lob_out['Mailing Status'])
lob_out['Mailing Status'] = np.where(lob_out['Mailing Status'] =='N','Undeliverable', lob_out['Mailing Status'])
lob_out.head()


# # Merging Lob Verification to the Mother File

# In[25]:


new_df = df.merge(lob_out, on=['SL no'], how ='left')

# col1_name=["OWNER MAILING NAME_y"]
# for i in range(len(col1_name)):
#     first1_col = new_df.pop(col1_name[i])
    
# col_name="Mailing Status"
# first_col = new_df.pop(col_name)
# new_df.insert(0, col_name, first_col)


# In[26]:


#new_df = new_df.sort_values("OWNER MAILING NAME")
#new_df.to_csv('Acc_in.csv',index = False)


# In[27]:


new_df[["OWNER MAILING NAME_x","Mailing Status","MAILING STREET ADDRESS_x"]]


# In[28]:


new_df


# # Defining The Reference Number

# In[29]:


new_df = new_df.rename(columns={"APN - FORMATTED" : "APN"})


# In[32]:


ref = input('What is the Serial number? ')
ref = int(ref)
ref_df = new_df
ref_df['Old Reference'] = range(ref, ref+len(ref_df))

col_name="Old Reference"
first_col = ref_df.pop(col_name)
ref_df.insert(0, col_name, first_col)


# In[33]:


ref_df


# In[35]:


num = input('What is the Campaign Number? ')
num = int(num)

ref_df = ref_df.assign(Campaign_Number = num, Acquisition_Manager=np.nan, Owner_Type=np.nan)
ref_df = ref_df.rename(columns={"Campaign_Number" :"Campaign Number"})
ref_df = ref_df.rename(columns={"OWNER MAILING NAME_y":"OWNER MAILING NAME",
                                "MAIL CITY_y" :"MAIL CITY",
                                "MAILING STREET ADDRESS_y":"MAILING STREET ADDRESS",
                                "MAIL STATE_y" : "MAIL STATE",
                                "MAIL ZIP/ZIP+4_y" : "MAIL ZIP/ZIP+4"})
#ref_df = ref_df.rename(columns={"Acquisition_Manager" :"Acquisition Manager"})

'''col_name="Acquisition Manager"
first_col = ref_df.pop(col_name)
ref_df.insert(0, col_name, first_col)'''


# In[36]:


ref_df.head()


# # Dividing the data into company and individual

# In[37]:


'''cmpny = ref_df[(ref_df['OWNER 1 TYPE'] == "Corporate") | (ref_df['OWNER 1 TYPE'] == "CORPORATE")]
col_name="Owner_Type"
first_col = ref_df.pop(col_name)
ref_df.insert(0, col_name, first_col)

cmpny = cmpny.assign(Owner_Type='C')
indi = ref_df[(ref_df['OWNER 1 TYPE'] == "Individual") | (ref_df['OWNER 1 TYPE'] == "INDIVIDUAL")]
indi = indi.assign(Owner_Type='I')
frames = [cmpny, indi]

final_ref_df = pd.concat(frames)

final_ref_df = final_ref_df.sort_values('Old Reference')'''


# In[38]:


final_ref_df=ref_df


# In[39]:


final_ref_df["Owner_Type"]


# In[40]:


ref_df = final_ref_df
ref_df["LOT ACREAGE"].count()


# In[41]:


ref_df.head()


# In[42]:


col_name="Acquisition_Manager"
first_col = ref_df.pop(col_name)
ref_df.insert(0, col_name, first_col)
ref_df


# # Filtering the Data Based on Acquistions Manager

# In[43]:


filter_criteria_1 = ref_df['LOT ACREAGE'] <= 5
test = ref_df[filter_criteria_1]
#test.sort_values('APN')


# In[44]:


df_split = test.sample(frac=0.5,random_state=200)
#df_split.sort_values(by="APN - FORMATTED")


# In[45]:


df_split


# In[46]:


df_new = pd.concat([test, df_split]).drop_duplicates(keep=False)


# In[47]:


#df_new.sort_values(by="APN - FORMATTED")


# In[48]:


df_split = df_split.assign(Acquisition_Manager= '1')
df_new = df_new.assign(Acquisition_Manager= '2')


# In[49]:


df_split


# In[50]:


df_new.head()


# In[51]:


final_1 = pd.concat([df_new, df_split]).drop_duplicates(keep=False)


# In[52]:


final_1.head()


# In[53]:


filter_criteria_2 = ref_df['LOT ACREAGE'] > 5
test2 = ref_df[filter_criteria_2]
#test2.sort_values("APN - FORMATTED")


# In[54]:


final_2 = test2.assign(Acquisition_Manager= '3')


# In[55]:


final = pd.concat([final_1, final_2]).drop_duplicates(keep=False)
#final.sort_values(by = 'Old Reference')


# In[56]:


final[["OWNER MAILING NAME","LOT ACREAGE","Acquisition_Manager"]]


# # Creating The Final Reference Number

# In[57]:


#final_ref_df['Old Reference'] = final_ref_df['Old Reference'].astype(str)
final['Campaign Number'] = final['Campaign Number'].astype(str)
final['Acquisition Manager'] = final['Acquisition_Manager'].astype(str)
final = final.assign(Reference=np.nan)


# In[58]:


final


# In[59]:


cols = ['Acquisition Manager', 'Old Reference','Campaign Number']
final['Reference'] = final[cols].apply(lambda row: ''.join(row.values.astype(str)), axis=1)


# In[60]:


col_name="Reference"
first_col = final.pop(col_name)
final.insert(0, col_name, first_col)


# In[61]:


final


# In[62]:


#ref_df.pop('Reference') #AGER REFERENCE NUMBER MUCHTE HOLE


# In[63]:


fin_ref_df = final


# In[64]:


#fin_ref_df.to_excel('Clean data of campaign.xlsx')


# # Pricing Agent's File Format

# In[65]:


selected_columns = fin_ref_df[["APN",
                           "LOT ACREAGE",
                            "Owner_Type",
                           "COUNTY",
                           "MARKET TOTAL VALUE",
                           "SITUS STREET ADDRESS",
                           "SITUS CITY",
                           "SITUS ZIP+4",
                           "SITUS ZIP CODE",
                           "SITUS STATE",
                           "OWNER MAILING NAME",
                           "Mailing Status",
                           "Old Reference",
                           "Reference",
                           "Campaign Number",
                           "MAILING STREET ADDRESS",
                           "MAIL CITY",
                           "MAIL STATE",
                           "MAIL ZIP/ZIP+4",
                           "APN - UNFORMATTED",
                           "ALTERNATE APN",
                           "LOT AREA",
                           "LEGAL DESCRIPTION",
                           "SCHOOL DISTRICT 1",
                           "LATITUDE",
                           "LONGITUDE"]]
new_df = selected_columns.copy()


# In[66]:


of2ow_df = new_df.rename(columns={"Reference" :"«Reference»" ,
                                    "COUNTY" :"«County_Name»" ,
                                    "OWNER MAILING NAME" : "«Owner_Name»",
                                    "MAILING STREET ADDRESS" : "«Mail_Address»",
                                    "MAIL CITY" : "«Mail_City»",
                                    "MAIL STATE" : "«Mail_State»",
                                    "MAIL ZIP/ZIP+4" : "«Mail_ZIP_Code»",
                                    "SITUS STATE" : "«State»" ,
                                    "APN" : "«APN»",
                                      "ALTERNATE APN" : "Alt/Old APN",
                                  "APN - UNFORMATTED" : "APN Unformatted",
                                    "LOT ACREAGE" : "«Lot_Acreage»",
                                   "LEGAL DESCRIPTION" : "«Legal_Description»",
                                    "MARKET TOTAL VALUE" : "parval",
                                    "SITUS CITY" : "Site City",
                                    "SITUS ZIP CODE" : "Site ZIP",
                                    "SITUS STREET ADDRESS" : "Site Address",
                                    "LATITUDE" : "lat",
                                     "LONGITUDE" : "lon"})
of2ow_df


# In[67]:


selected_columns = of2ow_df[["«APN»",
                           "«Reference»",
                           "Campaign Number",
                           "Owner_Type",
                           "Mailing Status",
                           "Old Reference",
                           "«County_Name»",
                           "«Owner_Name»",
                           "«Mail_Address»",
                           "«Mail_City»",
                           "«Mail_State»",
                           "«Mail_ZIP_Code»",
                           "«State»",
                           "APN Unformatted",
                           "Alt/Old APN",
                           "«Lot_Acreage»",
                           "«Legal_Description»",
                           "parval",
                           "Site City",
                           "Site ZIP", 
                           "Site Address",
                           "lat",
                           "lon"
                          ]]
of2ow_df = selected_columns.copy()


# In[68]:


of2ow_df.head()


# In[69]:


LandQuire_df=of2ow_df.copy()
LandQuire_df['«County_Name»'] = LandQuire_df['«County_Name»'].astype(str).str.cat(LandQuire_df['«State»'].astype(str), sep=', ')


# In[70]:


LandQuire_df.head()


# In[71]:


LandQuire_df = LandQuire_df.sort_values(['Old Reference'], ascending=[True])


LandQuire_df["lat"] = LandQuire_df["lat"].replace(to_replace=0, method='ffill')
LandQuire_df["lon"] = LandQuire_df["lon"].replace(to_replace=0, method='ffill')


# In[72]:


LandQuire_df.columns


# In[73]:


LandQuire_df[LandQuire_df['Mailing Status']=='Deliverable'].to_excel('offers2owners.xlsx',index=False)
LandQuire_df[LandQuire_df['Mailing Status']=='Undeliverable'].to_excel(r'E:\LandQuire\3. Undeliverable Data\Main Data\Undeliverable.xlsx',index=False)

