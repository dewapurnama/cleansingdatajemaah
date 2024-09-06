import streamlit as st
import pandas as pd
import regex as re
import numpy as np
import io

# Title of the app
st.title('Cleansing Data Transaksi Jemaah')

# Upload BRJ file
brj_file = st.file_uploader("Upload File BRJ disini", type=['xls', 'xlsx'])
if brj_file is not None:
    df_brj = pd.read_excel(brj_file)
    # Only select necessary columns to reduce memory usage
    df_brj = df_brj[['description', 'tx_code', 'jenis_mutasi', 'nilai_mutasi', 'nomrek_lawan_asli']]

    st.write(f"Menampilkan {min(len(df_brj), 100)} baris pertama dari total {len(df_brj)} baris.")
    st.dataframe(df_brj.head(100))

    # Define extraction function
    def extract_number(text):
        text = str(text)
        matches = re.findall(r'\d{9,}', text)
        return min(matches, key=len) if matches else None

    # Apply the function using .loc to avoid warnings
    df_brj.loc[:, 'parsing_deskripsi'] = df_brj['description'].apply(extract_number)

    # Add '0' in front if the number has 9 digits
    df_brj.loc[:, 'parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))
    
    # Add '0' in front if the number has 9 digits
    df_brj.loc[:, 'nomrek_lawan_asli_updated'] = df_brj['nomrek_lawan_asli'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))

    # Modify values
    def modify_value(val):
        val_str = str(val)
        if len(val_str) > 10 and val_str.startswith('0'):
            stripped_val = val_str.lstrip('0')
            return stripped_val.zfill(10) if len(stripped_val) <= 10 else stripped_val
        return val_str

    df_brj.loc[:, 'parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(modify_value)

    # Filter DataFrame
    filtered_df_brj = df_brj[df_brj['tx_code'].isin(['BTAW', 'BTVL', 'BTLN', 'KMLN', 'KMNM', 'MEB', 'PK'])]

    # Ensure columns are strings
    filtered_df_brj.loc[:, 'parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].astype(str)
    filtered_df_brj.loc[:, 'nomrek_lawan_asli_updated'] = filtered_df_brj['nomrek_lawan_asli_updated'].astype(str)

    # Replace 'None' with NaN
    filtered_df_brj.loc[:, 'parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].replace('None', np.nan)

    # Fill NaN values
    filtered_df_brj.loc[:, 'parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].fillna(filtered_df_brj['nomrek_lawan_asli_updated'])

# Upload SPM file
spm_file = st.file_uploader("Upload File SPM disini", type=['xls', 'xlsx'])
if spm_file is not None:
    df_spm = pd.read_excel(spm_file)
    st.write(f"Menampilkan {min(len(df_spm), 100)} baris pertama dari total {len(df_spm)} baris.")
    st.dataframe(df_spm.head(100))

    # Apply the function to the columns
    df_spm.loc[:, 'no_porsi'] = df_spm['no_porsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))
    df_spm.loc[:, 'no_rekening'] = df_spm['no_rekening'].apply(modify_value)
    df_spm.loc[:, 'no_validasi'] = df_spm['no_validasi'].apply(modify_value)

    # Calculate the sum of nilai_mutasi for C and D
    grouped = filtered_df_brj.groupby('parsing_deskripsi', as_index=False, group_keys=False).apply(
        lambda x: pd.Series({
            'sum_C': x.loc[x['jenis_mutasi'] == 'C', 'nilai_mutasi'].sum(),
            'sum_D': x.loc[x['jenis_mutasi'] == 'D', 'nilai_mutasi'].sum()
        })
    ).reset_index()

    filtered_df_brj = filtered_df_brj.merge(grouped, on='parsing_deskripsi')
    filtered_df_brj['total_mutasi'] = (filtered_df_brj['sum_C'] - filtered_df_brj['sum_D']).abs()
    filtered_df_brj.drop(['sum_C', 'sum_D'], axis=1, inplace=True)

    # Perform merges
    merged_df1 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_validasi', how='inner')
    merged_df2 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_porsi', how='inner')
    merged_df3 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_rekening', how='inner')
    merged_df4 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='inner')
    merged_df5 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_porsi', how='inner')
    merged_df6 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_validasi', how='left')

    # Concatenate and drop duplicates
    concatenated_df = pd.concat([merged_df1, merged_df2, merged_df3, merged_df4, merged_df5, merged_df6], ignore_index=True)
    result = concatenated_df.drop_duplicates(subset='id_brj', keep='first')

    # Perform outer merges to find unmatched rows
    merged_df7 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_porsi', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj1 = merged_df7[merged_df7['_merge'] == 'right_only'].drop(columns=['_merge'])

    merged_df8 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_validasi', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj2 = merged_df8[merged_df8['_merge'] == 'right_only'].drop(columns=['_merge'])

    merged_df9 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj3 = merged_df9[merged_df9['_merge'] == 'right_only'].drop(columns=['_merge'])

    merged_df10 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_validasi', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj4 = merged_df10[merged_df10['_merge'] == 'right_only'].drop(columns=['_merge'])

    merged_df11 = filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on='no_porsi', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj5 = merged_df11[merged_df11['_merge'] == 'right_only'].drop(columns=['_merge'])

    merged_df12 = filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on='no_rekening', how='outer', indicator=True)
    df_spm_not_in_filtered_df_brj6 = merged_df12[merged_df12['_merge'] == 'right_only'].drop(columns=['_merge'])

    # Concatenate unmatched rows
    concatenated_df2 = pd.concat([df_spm_not_in_filtered_df_brj1, df_spm_not_in_filtered_df_brj2, 
                                  df_spm_not_in_filtered_df_brj3, df_spm_not_in_filtered_df_brj4, 
                                  df_spm_not_in_filtered_df_brj5, df_spm_not_in_filtered_df_brj6], ignore_index=True)
    result2 = concatenated_df2.drop_duplicates(subset=['tanggal_SPM', 'no_SPM', 'nama_jamaah'], keep='first')

    # Prepare download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        result2.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()

    st.write(f"Download data yang sudah dicleansing di bawah ini")
    st.download_button(
        label="Download data as Excel",
        data=buffer,
        file_name='Data_Pembatalan_Bersih.xlsx',
        mime='application/vnd.ms-excel'
    )
