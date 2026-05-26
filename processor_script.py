import pandas as pd
import numpy as np

class Processer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        # self.df = None

    def csv_loader(self, path):
        df = pd.read_csv(path)
        return df

    def column_standardise(self, df):
        # Standardise column names
        df.columns = df.columns.str.replace(' ', '_').str.lower()
        df = df.rename(columns={'d.o.b': 'date_of_birth', 'nationality(/ies)': 'nationality'})

        # Convert columns dtype to datetime
        df['last_updated'] = pd.to_datetime(df['last_updated'], dayfirst=True)
        df['date_designated'] = pd.to_datetime(df['date_designated'], dayfirst=True)
        # Standardise casing
        df['name_type'] = df['name_type'].str.title()
        # dtype to Int64 (allows null vals)
        df['ofsi_group_id'] = df['ofsi_group_id'].astype('Int64')

        # Clean whitespace and punctuation
        cols = ['national_identifier_number', 'passport_number']
        df[cols] = (
            df[cols]
            .astype('str')
            # .apply(lambda x: x.str.replace('[^a-zA-Z0-9]', '', regex=True)) # google to check standards of it
            .apply(lambda x: x.str.strip())
        )
        return df


    def target_data(self, df):
        designation_drop = df[df['Designation Type'].isin(['Entity', 'Ship'])].index
        df.drop(designation_drop, inplace=True)
        return df

    def combine_fields(self, df):
        # name_1: first name, name_2-5: other/middle names, name_6: surname
        name_cols = ['name_1', 'name_2', 'name_3', 'name_4', 'name_5', 'name_6']
        address_col = ['address_line_1','address_line_2','address_line_3','address_line_4','address_line_5','address_line_6']
        # Apply standadising function of capitalising and cleaning whitespace
        df[name_cols] = df[name_cols].apply(lambda x: x.str.strip().str.title())
        # Combine into one field
        df['full_name'] = (df[name_cols]
            .apply(lambda x: x.str.strip().str.title())
            .apply(lambda row: ' '.join(x for x in row if pd.notna(x) and x), axis=1)
        )
        df['address'] = df[address_col].apply(
            lambda row: ', '.join(x.strip() for x in row if pd.notna(x) and str(x).strip()), axis=1
        )
        return df

    def run(self):
        df = self.csv_loader
        df_col_clean = self.column_standardise(df)

        # df.to_csv('clean_individuals.csv', index=False)



if __name__ == '__main__':
    clean = Processer('data/UK-Sanctions-List.csv')
    clean.run()