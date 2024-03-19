import os
import requests
import numpy as np
import pandas as pd

DATA_PATH = 'data/MMM_MMM_DAE.csv'

def download_data(url, force_download=False, ):
    # Utility function to donwload data if it is not in disk
    data_path = os.path.join('data', os.path.basename(url.split('?')[0]))
    if not os.path.exists(data_path) or force_download:
        # ensure data dir is created
        os.makedirs('data', exist_ok=True)
        # request data from url
        response = requests.get(url, allow_redirects=True)
        # save file
        with open(data_path, "w") as f:
            # Note the content of the response is in binary form: 
            # it needs to be decoded.
            # The response object also contains info about the encoding format
            # which we use as argument for the decoding
            f.write(response.content.decode(response.apparent_encoding))

    return data_path


def load_formatted_data(data_fname:str) -> pd.DataFrame:
    """ One function to read csv into a dataframe with appropriate types/formats.
        Note: read only pertinent columns, ignore the others.
    """
    df = pd.read_csv(data_fname)
    return df


# once they are all done, call them in the general sanitizing function
def sanitize_data(df:pd.DataFrame) -> pd.DataFrame:
    """ One function to do all sanitizing"""
    sanitize_adr_num_column(df)
    sanitize_adr_voie_column(df)
    sanitize_com_cp_column(df)
    sanitize_com_nom_column(df)
    sanitize_tel_column(df)
    sanitize_freq_mnt_columns(df)
    sanitize_dermnt_columns(df)
    sanitize_lat_coor1_columns(df)
    sanitize_long_coor1_columns(df)

    return df


# Define a framing function
def frame_data(df:pd.DataFrame) -> pd.DataFrame:
    """ One function all framing (column renaming, column merge)"""
    df.rename(...)
    ...
    return df


# once they are all done, call them in the general clean loading function
def load_clean_data(df:pd.DataFrame)-> pd.DataFrame:
    """one function to run it all and return a clean dataframe"""
    df = (df.pipe(load_formatted_data)
          .pipe(sanitize_data)
          .pipe(frame_data)
    )
    return df


def sanitize_adr_num_column(df):
    df['adr_num'] = pd.to_numeric(df['adr_num'], errors='coerce')
    mask_not_nan = ~df['adr_num'].isna()
    df.loc[mask_not_nan, 'adr_num'] = df.loc[mask_not_nan, 'adr_num'].astype(int)

def sanitize_adr_voie_column(df):
    df['adr_voie'] = df['adr_voie'].fillna('').astype(str)
    df['adr_voie'] = df['adr_voie'].str.strip()
    df['adr_voie'] = df['adr_voie'].replace(r'^-$', 'N/A', regex=True)
    df['adr_voie'] = df['adr_voie'].replace('', 'N/A')
    df['adr_voie'] = df['adr_voie'].fillna('N/A')

def sanitize_com_cp_column(df):
    pass

def sanitize_com_nom_column(df):
    df['com_nom'] = "Montpellier"

def sanitize_tel_column(df):
    extraction = df.tel1.str.extract(
        pat=r"\+*(?:33)0*(\d)\s*(\d\d)\s*(\d\d)\s*(\d\d)\s*(\d\d)",
        expand=True
    )
    df["tel1"] = "0" + extraction[0].str.cat(extraction[[i for i in range(1,5)]])

def sanitize_freq_mnt_columns(df):
    spell_error = ['tout les ans','Tout les ans','tous les ans','Tous les ans']
    #Checking for a date in the column
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'  # This pattern matches strings in the format YYYY-MM-DD
    # Use regular expression to find values resembling dates in the target column
    date_matches = df['freq_mnt'].astype(str).str.contains(date_pattern, na=False)
 
    # Filter rows where date-like values are found
    filtered_df = df[date_matches]
 
    #Switcheing the cells if a date found
    for index, row in filtered_df.iterrows():
        # Get the index of the current row
        idx = index
       
        # Check if the next cell contains 'Tous les ans'
        if df.at[idx, 'dermnt'] in spell_error:
            # Switch the values in the current and next cells
            df.at[idx, 'freq_mnt'], df.at[idx, 'dermnt'] = df.at[idx, 'dermnt'], df.at[idx, 'freq_mnt']
   
    #Making empty values None int the freq_mnt column
    df['freq_mnt'] = df['freq_mnt'].replace(' ' or '', None)
 
    #MAking the string the same value
    df['freq_mnt'] = df['freq_mnt'].apply(lambda x: 'Tous Les ans' if (x in spell_error) else x)
 
    #COnvering to str at the end
    df['freq_mnt'] = df['freq_mnt'].astype(str)
 
def sanitize_dermnt_columns(df):
    #Converting to date time with correct format and setting Nat for empty
    df['dermnt'] = pd.to_datetime(df['dermnt'], errors='coerce')

def sanitize_lat_coor1_columns(df):
    #Converting to numeric and setting NaN for empty
    df['lat_coor1'] = pd.to_numeric(df['lat_coor1'], errors='coerce')
   
def sanitize_long_coor1_columns(df):
    #Converting to numeric and setting NaN for empty
    df['long_coor1'] = pd.to_numeric(df['long_coor1'], errors='coerce')
   

# if the module is called, run the main loading function
if __name__ == '__main__':
    load_clean_data(download_data())