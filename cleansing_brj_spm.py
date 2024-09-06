import streamlit as st
import pandas as pd
import numpy as np
import io
import regex as re

# Title
st.title('Cleansing Data Transaksi Jemaah')

# File Upload
brj_file = st.file_uploader("Upload File BRJ disini", type=['xls', 'xlsx'])
spm_file = st.file_uploader("Upload File SPM disini", type=['xls', 'xlsx'])

if brj_file is not None:
    df_brj = pd.read_excel(brj_file)
    st.write(f"Menampilkan {min(len(df_brj), 100)} baris pertama dari total {len(df_brj)} baris.")
    st.dataframe(df_brj.head(100))

    # Extract and process 'parsing_deskripsi'
    def extract_number(text):
        text = str(text)
        matches = re.findall(r'\d{9,}', text)
        return min(matches, key=len) if matches else None

    df_brj['parsing_deskripsi'] = df_brj['description'].apply(extract_number)

    # Add '0' in front if the number has 9 digits
    df_brj['parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))
    
    # Add '0' in front if the number has 9 digits
    df_brj['nomrek_lawan_asli_updated'] = df_brj['nomrek_lawan_asli'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))

    # Modify values
    def modify_value(val):
        val_str = str(val)
        if len(val_str) > 10 and val_str.startswith('0'):
            stripped_val = val_str.lstrip('0')
            return stripped_val.zfill(10) if len(stripped_val) <= 10 else stripped_val
        return val_str

    df_brj['parsing_deskripsi'] = df_brj['parsing_deskripsi'].apply(modify_value)

    # Filter DataFrame
    filtered_df_brj = df_brj[df_brj['tx_code'].isin(['BTAW', 'BTVL', 'BTLN', 'KMLN', 'KMNM', 'MEB', 'PK'])]

    # Ensure columns are strings
    filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].astype(str)
    filtered_df_brj['nomrek_lawan_asli_updated'] = filtered_df_brj['nomrek_lawan_asli_updated'].astype(str)

    # Replace 'None' with NaN
    filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].replace('None', np.nan)

    # Fill NaN values
    filtered_df_brj['parsing_deskripsi'] = filtered_df_brj['parsing_deskripsi'].fillna(filtered_df_brj['nomrek_lawan_asli_updated'])

    if spm_file is not None:
        df_spm = pd.read_excel(spm_file)
        st.write(f"Menampilkan {min(len(df_spm), 100)} baris pertama dari total {len(df_spm)} baris.")
        st.dataframe(df_spm.head(100))

        # Apply transformations to df_spm
        df_spm['no_porsi'] = df_spm['no_porsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))
        df_spm['no_rekening'] = df_spm['no_rekening'].apply(modify_value)
        df_spm['no_validasi'] = df_spm['no_validasi'].apply(modify_value)

        # Calculate sums and merge
        grouped = filtered_df_brj.groupby('parsing_deskripsi').apply(
            lambda x: pd.Series({
                'sum_C': x.loc[x['jenis_mutasi'] == 'C', 'nilai_mutasi'].sum(),
                'sum_D': x.loc[x['jenis_mutasi'] == 'D', 'nilai_mutasi'].sum()
            })
        ).reset_index()

        filtered_df_brj = filtered_df_brj.merge(grouped, on='parsing_deskripsi')
        filtered_df_brj['total_mutasi'] = (filtered_df_brj['sum_C'] - filtered_df_brj['sum_D']).abs()
        filtered_df_brj.drop(['sum_C', 'sum_D'], axis=1, inplace=True)

        # Merge DataFrames
        merged_dfs = []
        for col in ['no_validasi', 'no_porsi', 'no_rekening']:
            merged_dfs.append(filtered_df_brj.merge(df_spm, left_on='parsing_deskripsi', right_on=col, how='inner'))
            merged_dfs.append(filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on=col, how='inner'))

        concatenated_df = pd.concat(merged_dfs, ignore_index=True)
        result = concatenated_df.drop_duplicates(subset='id_brj', keep='first')

        # Calculate unmatched records
        unmatched_dfs = []
        for col in ['no_validasi', 'no_porsi', 'no_rekening']:
            unmatched_dfs.append(filtered_df_brj.merge(df_spm, left_on='nomrek_lawan_asli_updated', right_on=col, how='outer', indicator=True)
                                 .query('_merge == "right_only"').drop(columns=['_merge']))

        concatenated_df2 = pd.concat(unmatched_dfs, ignore_index=True)
        result2 = concatenated_df2.drop_duplicates(subset=['tanggal_SPM', 'no_SPM', 'nama_jamaah'], keep='first')

        # Provide download option
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            result2.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()

        st.write("Download data yang sudah dicleansing di bawah ini")
        st.download_button(
            label="Download data as Excel",
            data=buffer.getvalue(),
            file_name='Data_Pembatalan_Bersih.xlsx',
            mime='application/vnd.ms-excel'
        )
