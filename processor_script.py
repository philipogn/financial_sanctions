import pandas as pd
import numpy as np

class Processer:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        # self.df = None


    def csv_loader(self, path):
        df = pd.read_csv(path, skiprows=1)
        return df


    def clean_drop_cols(self, df):
        # Standardise column names
        df.columns = (df.columns.
                      str.replace(' ', '_').
                      str.replace('-', '_').
                      str.lower()
        )
        df = df.rename(columns={'d.o.b': 'date_of_birth', 'nationality(/ies)': 'nationality'})
        # Drop Entity and Ship designations
        designation_drop = df[df['designation_type'].isin(['Entity', 'Ship'])].index
        df = df.drop(designation_drop)
        # Drop unrelated/unecessary columns
        df = df.drop(
            columns=[
                'name_non_latin_script','non_latin_script_type','non_latin_script_language',
                'other_information','passport_additional_information',
                # Organisation details
                'type_of_entity','subsidiaries','parent_company','business_registration_number_(s)',
                # Ship details
                'imo_number','current_owner/operator_(s)','previous_owner/operator_(s)',
                'current_believed_flag_of_ship','previous_flags','type_of_ship',
                'tonnage_of_ship','length_of_ship','year_built','hull_identification_number_(hin)'
            ]
        )
        df = df.drop_duplicates()
        return df


    def column_standardise(self, df):
        # Convert columns dtype to datetime
        df['last_updated'] = pd.to_datetime(df['last_updated'], dayfirst=True)
        df['date_designated'] = pd.to_datetime(df['date_designated'], dayfirst=True)
        # dtype to Int64 (allows null values, could leave as float)
        df['ofsi_group_id'] = df['ofsi_group_id'].astype('Int64')

        # Clean up whitespace and replace uncommon unicode
        text_columns = df.select_dtypes(include='string').columns
        for col in text_columns:
            df[col] = (
                df[col]
                .astype('string')
                .str.replace("\u2018", "'", regex=False) # open apostrophe
                .str.replace("\u2019", "'", regex=False) # closed apostrophe
                .str.replace("\u2013", "-", regex=False) # dash
                .str.replace(r'\s+', ' ', regex=True)
                .str.strip()
            )
        
        # Standardise casing
        df['name_type'] = df['name_type'].str.title()
        df['gender'] = df['gender'].str.title()
        df['town_of_birth'] = df['town_of_birth'].str.title()
        return df


    def combine_fields(self, df):
        # name_1: first name, name_2-5: other/middle names, name_6: surname
        name_cols = ['name_1', 'name_2', 'name_3', 'name_4', 'name_5', 'name_6']
        address_col = ['address_line_1','address_line_2','address_line_3','address_line_4','address_line_5','address_line_6']
        # Combine into one field
        df['full_name'] = (
            df[name_cols]
            .apply(lambda x: x.str.title())
            .apply(lambda row: ' '.join(x for x in row if pd.notna(x) and x), axis=1)
        )
        df['address'] = (
            df[address_col]
            .apply(lambda row: ' '.join(x for x in row if pd.notna(x) and x), axis=1)
        )
        return df


    def combine_ids(self, df):
        primary_df = (df[(df['name_type'] == 'Primary Name') & 
                         (df['full_name'].notna()) &
                         (df['full_name'].str.strip() != '')]
                         .drop_duplicates(subset=['unique_id'])
                         .copy()
        )
        # Extract only full_name for aliases and group by unique_id
        aliases_df = (
            df[(df['name_type'] == 'Alias') |
               (df['name_type'] == 'Primary Name Variation')]
            .groupby('unique_id')['full_name']
            .apply(lambda x: '|'.join(sorted(set(x))))
            .reset_index()
            .rename(columns={'full_name': 'aliases'})
        )
        aggregated_df = df.groupby('unique_id').agg({
            'date_of_birth': self._combine_unique,
            'nationality': self._combine_unique,
            'town_of_birth': self._combine_unique,
            'passport_number': self._combine_unique,
            'national_identifier_number': self._combine_unique,
            'address': self._combine_unique,
            'address_country': self._combine_unique,
            # 'sanctions_imposed': self._combine_unique, # no uniques per id, remove
            'position': self._combine_unique
        }).reset_index()

        # Drop not aggregated original df columns
        aggregate_cols = [
            'date_of_birth', 'nationality', 'town_of_birth', 'passport_number',
            'national_identifier_number', 'address', 'address_country', 'position'
        ]
        primary_df = primary_df.drop(columns=aggregate_cols, errors='ignore')

        final_df = (primary_df
                    .merge(aliases_df, on='unique_id', how='left')
                    .merge(aggregated_df, on='unique_id', how='left')
        )
        final_df = final_df.rename(columns={'full_name': 'primary_name'})
        final_df = final_df[
            ['unique_id','ofsi_group_id', 'primary_name', 'aliases',
            'date_of_birth','nationality','gender','town_of_birth','country_of_birth',
            'phone_number','email_address', 'national_identifier_number','passport_number',
            'address','address_postal_code','address_country',
            'regime_name','designation_source','date_designated','sanctions_imposed',
            'position','last_updated', ]
        ]
        # final_df.to_csv('../data/final.csv', index=False)
        return final_df


    def _combine_unique(self, values): # Helper function aggregate cols with multiple values
        return '|'.join(sorted(set(v for v in values if pd.notna(v) and v)))


    def run(self):
        df = self.csv_loader(self.csv_path)
        df = self.clean_drop_cols(df)
        df_col_clean = self.column_standardise(df)
        df_combined = self.combine_fields(df_col_clean)
        df_final = self.combine_ids(df_combined)

        df_final.to_csv('individual_sanctions.csv', index=False)


if __name__ == '__main__':
    clean = Processer('data/UK-Sanctions-List.csv')
    clean.run()