#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
import regex as re
import numpy as np
import io
import xlsxwriter
import openpyxl

# In[2]:

st.title('Cleansing Data Transaksi Jemaah')

brj_file = st.file_uploader("Upload File BRJ disini", type=['xls','xlsx'])
buffer = io.BytesIO()
if brj_file is not None:
    brj = pd.read_excel(brj_file)
    st.dataframe(brj)
#df_brj = pd.read_excel('C:/Users/User/Documents/ODP BPKH/OJT/A2/Cleansing BTAW/ibbankreportjournal_2022.xlsx')


# In[3]:


#df_brj


# In[4]:


#df_spm = pd.read_excel('C:/Users/User/Documents/ODP BPKH/OJT/A2/Cleansing BTAW/SPM-OK.xlsx')


# In[5]:


#df_spm


# In[6]:


# Function to extract the shortest sequence of 9 or more digits
#def extract_number(text):
    # Ensure the input is a string
   # text = str(text)
    # Find all sequences of 9 or more digits
    #matches = re.findall(r'\d{9,}', text)
    #if matches:
        # Return the shortest sequence
        #return min(matches, key=len)
    #else:
        #return None

# Apply the function to the DataFrame
#df_brj['parsing_deskripsi'] = df_brj['description'].apply(extract_number)


# In[7]:


# Function to add '0' in front if the number has 9 digits
#df_brj['parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))

#df_brj


# In[8]:


# Function to add '0' in front if the number has 9 digits
#df_brj['nomrek_lawan_asli_updated'] = df_brj['nomrek_lawan_asli'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))

#df_brj


# In[9]:


#def modify_value(val):
    # Convert to string to handle leading zeros
    #val_str = str(val)
    
    # Check if the value has more than 10 digits and begins with '0'
    #if len(val_str) > 10 and val_str.startswith('0'):
        # Strip leading zeros and ensure it's 10 digits long
        #stripped_val = val_str.lstrip('0')
        # If stripping leaves it with fewer than 10 digits, add leading zeros
        #if len(stripped_val) <= 10:
            #return stripped_val.zfill(10)
        #else:
            #return stripped_val
    #else:
        #return val_str

# Apply the function to the column
#df_brj['parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(modify_value)


# In[10]:


#df_brj.dtypes


# In[11]:


# Filter the DataFrame to keep only the rows with the specified tx_code values
#filtered_df_brj = df_brj[df_brj['tx_code'].isin(['BTAW', 'BTVL', 'BTLN', 'KMLN', 'KMNM', 'MEB', 'PK'])]
#filtered_df_brj


# In[12]:


# Ensure columns are strings
#filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].astype(str)
#filtered_df_brj['nomrek_lawan_asli_updated'] = filtered_df_brj['nomrek_lawan_asli_updated'].astype(str)

# Replace the string 'None' with actual NaN
#filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].replace('None', np.nan)

# Fill NaN values in 'parsing_deskripsi' with values from 'nomrek_lawan_asli_updated'
#filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].fillna(filtered_df_brj['nomrek_lawan_asli_updated'])


# In[13]:


#filtered_df_brj.iloc[60908]


# In[14]:


#filtered_df_brj.dtypes


# In[15]:


#df_spm.columns


# In[16]:


# Function to add '0' in front if the number has 9 digits
#df_spm['no_porsi'] = df_spm['no_porsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))

#df_spm


# In[17]:


# Apply the function to the column
#df_spm['no_rekening'] = df_spm['no_rekening'].apply(modify_value)


# In[18]:


#df_spm


# In[19]:


#df_spm['no_validasi'] = df_spm['no_validasi'].apply(modify_value)


# In[20]:


# Calculate the sum of nilai_mutasi for C and D
#grouped = filtered_df_brj.groupby('parsing_deskripsi').apply(
    #lambda x: pd.Series({
        #'sum_C': x.loc[x['jenis_mutasi'] == 'C', 'nilai_mutasi'].sum(),
        #'sum_D': x.loc[x['jenis_mutasi'] == 'D', 'nilai_mutasi'].sum()
    #})
#).reset_index()

# Merge the sum_C and sum_D with the original DataFrame
#filtered_df_brj = filtered_df_brj.merge(grouped, on='parsing_deskripsi')

# Calculate total_mutasi as the absolute difference
#filtered_df_brj['total_mutasi'] = (filtered_df_brj['sum_C'] - filtered_df_brj['sum_D']).abs()

# Drop the intermediate columns
#filtered_df_brj.drop(['sum_C', 'sum_D'], axis=1, inplace=True)


# In[24]:


#filtered_df_brj


# In[29]:


# Perform the merge
#merged_df1 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_validasi', how='inner')
# Perform the merge
#merged_df2 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_porsi', how='inner')
# Perform the merge
#merged_df3 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_rekening', how='inner')
# Perform the merge
#merged_df4 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='inner')
# Perform the merge
#merged_df5 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_porsi', how='inner')
# Perform the merge
#merged_df6 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_validasi', how='left')


# In[30]:


# Assuming your DataFrames are named df1, df2, df3, df4, df5, and df6
#concatenated_df = pd.concat([merged_df1, merged_df2, merged_df3, merged_df4, merged_df5, merged_df6], ignore_index=True)

# Drop duplicates based on `id_brj`
#result = concatenated_df.drop_duplicates(subset='id_brj', keep='first')
#result


# In[41]:


# Perform an outer merge
#merged_df7 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_porsi', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj1 = merged_df7[merged_df7['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj1 = df_spm_not_in_filtered_df_brj1.drop(columns=['_merge'])

# Perform an outer merge
#merged_df8 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_validasi', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj2 = merged_df8[merged_df8['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj2 = df_spm_not_in_filtered_df_brj2.drop(columns=['_merge'])

# Perform an outer merge
#merged_df9 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj3 = merged_df9[merged_df9['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj3 = df_spm_not_in_filtered_df_brj3.drop(columns=['_merge'])

# Perform an outer merge
#merged_df10 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_validasi', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj4 = merged_df10[merged_df10['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj4 = df_spm_not_in_filtered_df_brj4.drop(columns=['_merge'])

# Perform an outer merge
#merged_df11 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_porsi', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj5 = merged_df11[merged_df11['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj5 = df_spm_not_in_filtered_df_brj5.drop(columns=['_merge'])

# Perform an outer merge
#merged_df12 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='outer', indicator=True)
# Filter to keep only rows from df_spm that do not have a match in filtered_df_brj
#df_spm_not_in_filtered_df_brj6 = merged_df12[merged_df12['_merge'] == 'right_only']
# Optionally drop the _merge column if you don't need it
#df_spm_not_in_filtered_df_brj6 = df_spm_not_in_filtered_df_brj6.drop(columns=['_merge'])


# In[42]:


# Assuming your DataFrames are named df1, df2, df3, df4, df5, and df6
#concatenated_df2 = pd.concat([df_spm_not_in_filtered_df_brj1, df_spm_not_in_filtered_df_brj2, 
                              #df_spm_not_in_filtered_df_brj3, df_spm_not_in_filtered_df_brj4, 
                              #df_spm_not_in_filtered_df_brj5, df_spm_not_in_filtered_df_brj6], ignore_index=True)
#concatenated_df2


# In[43]:


# Drop duplicates based on `id_brj`
#result2 = concatenated_df2.drop_duplicates(subset=['tanggal_SPM', 'no_SPM', 'nama_jamaah'], keep='first')
#result2


# In[37]:


# Perform the merge
#merged_df7 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_validasi', how='right')
#merged_df7


# In[39]:


# Filter rows where id_brj is missing
#filtered_merged_df7 = merged_df7 [merged_df7['id_brj'].isna()]

# Display the result
#filtered_merged_df7 


# In[44]:


#output_directory = 'C:/Users/User/Documents/ODP BPKH/OJT/A2/Cleansing BTAW/'
#output_filename = 'cek_merge_spm.xlsx'
#output_path = output_directory + output_filename

#result2.to_excel(output_path, index=False)


# In[ ]:




