import streamlit as st
import pandas as pd
import regex as re
import numpy as np
import io
import matplotlib.pyplot as plt

# Title of the app
st.title('Cleansing Data Transaksi Jemaah')

# Upload BRJ file
brj_file = st.file_uploader("Upload File BRJ disini", type=['xls', 'xlsx'])
if brj_file is not None:
    df_brj = pd.read_excel(brj_file)
    
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

    def modify_value(val):
    # Convert to string to handle leading zeros
        val_str = str(val)
    
    # Check if the value has more than 10 digits and begins with '0'
        if len(val_str) > 10 and val_str.startswith('0'):
            # Strip leading zeros and ensure it's 10 digits long
            stripped_val = val_str.lstrip('0')
            # If stripping leaves it with fewer than 10 digits, add leading zeros
            if len(stripped_val) <= 10:
                return stripped_val.zfill(10)
            else:
                return stripped_val
        else:
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
    dtype_spec = {
        'no_rekening': str,
        'no_validasi': str,
        'no_porsi': str
    }
    df_spm = pd.read_excel(spm_file, dtype=dtype_spec)
    st.write(f"Menampilkan {min(len(df_spm), 100)} baris pertama dari total {len(df_spm)} baris.")
    st.dataframe(df_spm.head(100))

    # Apply the function to the columns
    df_spm.loc[:, 'no_porsi'] = df_spm['no_porsi'].apply(lambda x: f'0{x}' if len(str(x)) == 9 else str(x))
    df_spm.loc[:, 'no_rekening'] = df_spm['no_rekening'].apply(modify_value)
    df_spm.loc[:, 'no_validasi'] = df_spm['no_validasi'].apply(modify_value)
    df_spm.loc['no_porsi'] = df_spm['no_porsi'].apply(modify_value)

    # Calculate the sum of nilai_mutasi for C and D
    grouped = filtered_df_brj.groupby('parsing_deskripsi', as_index=False, group_keys=False).apply(
    lambda x: pd.Series({
        'sum_C': x.loc[x['jenis_mutasi'] == 'C', 'nilai_mutasi'].sum(),
        'sum_D': x.loc[x['jenis_mutasi'] == 'D', 'nilai_mutasi'].sum()
    })).reset_index()

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

    # Ensure df is a copy if it's a slice of another DataFrame
    result = result.copy()

    # Create the new column 'nominal_status' based on the comparison using .loc
    result.loc[:, 'nominal_status'] = result.apply(
        lambda row: 'MATCH' if row['total_mutasi'] == row['total_nominal'] else 'CHECK',
        axis=1
    )

    # Extract the number after the period using regex
    result['parsing_nomrek_lawan'] = result['nomor_rekening_lawan'].str.extract(r'\.(\d+)')
    cols = result.columns.tolist()
    cols.insert(11, cols.pop(cols.index('parsing_nomrek_lawan')))
    result = result[cols]
    # Apply the function to the column
    result['parsing_nomrek_lawan'] = result['parsing_nomrek_lawan'].apply(modify_value)

    # Define the function to determine porsi_status
    def determine_status(row):
        if row['parsing_nomrek_lawan'] in [row['no_rekening'], row['no_validasi'], row['no_porsi']]:
            return 'MATCH'
        else:
            return 'CHECK'
    
    # Create the 'porsi_status' column
    result['porsi_status'] = result.apply(determine_status, axis=1)
    # Determine the final status
    result['final_status'] = result.apply(lambda row: 'Sesuai' if row['nominal_status'] == 'MATCH' and row['porsi_status'] == 'MATCH' else 'Tidak Sesuai', axis=1)
            
    def generate_saran_perbaikan(row):
        # Convert 'nan' strings to actual NaN values for easier handling
        no_porsi = row['no_porsi'] if row['no_porsi'] != 'nan' else None
        no_rekening = row['no_rekening'] if row['no_rekening'] != 'nan' else None
    
        if row['final_status'] == 'Sesuai':
            return "tidak perlu perbaikan"
        
        if row['nominal_status'] == 'CHECK' and row['porsi_status'] == 'CHECK':
            if pd.notna(row['nama_jamaah_SPM']):
                return "perlu pengecekan manual"
            else:
                return "tidak ada SPM-nya"
        
        if row['nominal_status'] == 'CHECK':
            difference = row['total_mutasi'] - row['nilai_mutasi']
            if difference < 0:
                return f"retur sebesar {abs(difference)}"
            else:
                return f"selisih sebesar {difference} tidak ada pada SPM"
        
        if row['porsi_status'] == 'CHECK':
            if no_porsi is not None:
                return f"nomor_rekening_lawan diupdate dengan {no_porsi} pada id_brj {row['id_brj']}"
            elif no_rekening is not None:
                return f"nomor_rekening_lawan diupdate dengan {no_rekening} pada id_brj {row['id_brj']}"
            else:
                return "perlu pengecekan manual"
        
        return "perlu pengecekan manual"

    # Apply the function to generate saran_perbaikan
    result['saran_perbaikan'] = result.apply(generate_saran_perbaikan, axis=1)

    # Prepare pie chart data
    status_counts = result['final_status'].value_counts()

    # Create two columns for layout
    col1, col2 = st.columns(2)

    with col1:
        # Plot the pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=['#66c2a5', '#fc8d62'])
        ax.set_title('Status Distribution')
        st.pyplot(fig)  # Display the pie chart in Streamlit

    with col2:
        if 'BPS' in result.columns and 'final_status' in result.columns:
            # Filter DataFrame for rows where final_status is 'Tidak Sesuai'
            filtered_result = result[result['final_status'] == 'Tidak Sesuai']
            
            # Count occurrences of each unique value in the BPS column
            bps_counts = filtered_result['BPS'].value_counts()
            # Sort counts in ascending order
            bps_counts = bps_counts.sort_values(ascending=True)
            
            # Plot the horizontal bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            bps_counts.plot(kind='barh', color='skyblue', ax=ax)
            ax.set_title('BPS Distribution for Tidak Sesuai')
            ax.set_xlabel('Count')
            ax.set_ylabel('BPS')
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            
            st.pyplot(fig)  # Display the horizontal bar chart in Streamlit
    
    # Prepare download
    st.dataframe(result)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        result.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()

    st.write(f"Download data yang sudah dicleansing di bawah ini")
    st.download_button(
        label="Download data as Excel",
        data=buffer,
        file_name='Data_Pembatalan_Bersih.xlsx',
        mime='application/vnd.ms-excel'
    )
