import pandas as pd
import sys
from abc import ABC, abstractmethod

# ===================== PARENT CLASS ======================
class SanctionsProcessor(ABC):
    # subclasses fills in
    designation_type = None
    output_path = None
    output_cols = []


    # Organisation details
    # 'type_of_entity','subsidiaries','parent_company','business_registration_number_(s)',
    # keep 'alias_strength' for strong alias
    aggregate_cols = [
            'date_of_birth', 'nationality', 'town_of_birth', 'country_of_birth',
            'phone_number', 'email_address', 'passport_number', 'national_identifier_number', 
            'address', 'address_postal_code', 'address_country', 'position'
        ]
    drop_columns=[
        'name_non_latin_script','non_latin_script_type','non_latin_script_language', 
        'uk_statement_of_reasons', 'un_reference_number','other_information',
        'national_identifier_additional_information', 'passport_additional_information',
        # Ship details
        'imo_number','current_owner/operator_(s)','previous_owner/operator_(s)',
        'current_believed_flag_of_ship','previous_flags','type_of_ship',
        'tonnage_of_ship','length_of_ship','year_built','hull_identification_number_(hin)'
    ]
    name_cols = ['name_1', 'name_2', 'name_3', 'name_4', 'name_5', 'name_6']
    address_cols = ['address_line_1','address_line_2','address_line_3','address_line_4','address_line_5','address_line_6']

    def __init__(self, csv_path):
        self.csv_path = csv_path


    def csv_loader(self, path):
        try:
            return pd.read_csv(path, skiprows=1, low_memory=False)
        except FileNotFoundError:
            print(f'File not found: {path}')
            sys.exit(1)


    def standardise_column_names(self, df):
        # Standardise column names
        df.columns = (
            df.columns.
            str.replace(' ', '_').
            str.replace('-', '_').
            str.lower()
        )
        df = df.rename(columns={'d.o.b': 'date_of_birth', 'nationality(/ies)': 'nationality'})
        return df

    def filter_designation(self):
        # to filter to designation (individual, entity)
        # and drop cols here?
        df = df[df['designation_type'] == self.designation_type].copy()
        df = df.drop(columns=self.drop_columns)
        return df.drop_duplicates()


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
                .str.replace("\u2018", "'", regex=False) # open apostrophe
                .str.replace("\u2019", "'", regex=False) # closed apostrophe
                .str.replace("\u2013", "-", regex=False) # dash
                .str.replace(r'\s+', ' ', regex=True)
                .str.strip()
            )

        # Standardise casing
        df['name_type'] = df['name_type'].str.title()
        return df


    def _join_cols(self, df, cols): # helper function to join values across columns
        return df[cols].apply(lambda row: ' '.join(x for x in row if pd.notna(x) and x), axis=1)

    def combine_fields(self, df):
        # name_1: first name, name_2-5: other/middle names, name_6: surname
        df['full_name'] = self._join_cols(self.name_cols).str.title()
        df['address'] = self._join_cols(self.address_cols)
        return df

    def _combine_unique(self, values): # Helper function aggregate cols with multiple values
        return '|'.join(sorted(set(v for v in values if pd.notna(v) and v)))

    def combine_ids(self, df):
        # Extract Primary Name where it exists per unique_id
        primary_df = (
            df[(df['name_type'] == 'Primary Name') & 
               (df['full_name'].notna()) &
               (df['full_name'] != '')]
               .drop_duplicates(subset=['unique_id'])
               .copy()
        )
        
        # Concat aliases and name variations into one field for each unique_id
        aliases_df = (
            df[(df['name_type'] == 'Alias') | 
               (df['name_type'] == 'Primary Name Variation')]
               .groupby('unique_id')['full_name']
               .apply(self._combine_unique)
               .reset_index()
               .rename(columns={'full_name': 'aliases'})
        )
        # Aggegate multiple possible values into one
        aggregated_df = df.groupby('unique_id').agg({col: self._combine_unique for col in self.aggregate_cols}).reset_index()

        # Drop unaggregated original df columns then merge aggregated columns
        primary_df = primary_df.drop(columns=self.aggregate_cols, errors='ignore')
        final_df = (primary_df
                    .merge(aliases_df, on='unique_id', how='left')
                    .merge(aggregated_df, on='unique_id', how='left')
        )

        final_df = final_df.rename(columns={'full_name': 'primary_name'})
        # final_df = final_df[
        #     ['unique_id','ofsi_group_id', 'primary_name', 'aliases',
        #     'date_of_birth','nationality','gender','town_of_birth','country_of_birth',
        #     'phone_number','email_address', 'national_identifier_number','passport_number',
        #     'address','address_postal_code','address_country',
        #     'regime_name','designation_source','date_designated','sanctions_imposed',
        #     'position','last_updated', ]
        # ]
        return final_df[self.output_cols]

    def save_csv(self, df):
        df.to_csv(self.output_path, index=False)


    def run(self):
        df = self.csv_loader(self.csv_path)
        df = self.standardise_column_names(df)
        df = self.filter_designation(df)
        df = self.column_standardise(df)
        df = self.combine_fields(df)
        df_final = self.combine_ids(df)
        self.save_csv(df_final)
        return df_final


# ===================== INDIVIDUAL CLASS ===================
class IndividualProcessor(SanctionsProcessor):
    designation_type = 'Individual'
    output_path = 'individual_sanctions.csv'
    output_cols = [
        'unique_id','ofsi_group_id', 'primary_name', 'aliases',
        'date_of_birth','nationality','gender','town_of_birth','country_of_birth',
        'phone_number','email_address', 'national_identifier_number','passport_number',
        'address','address_postal_code','address_country',
        'regime_name','designation_source','date_designated','sanctions_imposed',
        'position','last_updated'
    ]

    # implement this here
    # # Remove whitespace and leading apostrophe
    # for col in ['phone_number', 'national_identifier_number']:
    #     df[col] = df[col].str.lstrip("'").str.replace(r'\s+', '', regex=True)

    def column_standardise(self, df):
        df = super().column_standardise(df)
        # Remove whitespace and leading apostrophe
        for col in ['phone_number', 'national_identifier_number']:
            df[col] = df[col].str.lstrip("'").str.replace(r'\s+', '', regex=True)

        df['gender'] = df['gender'].str.title()
        df['town_of_birth'] = df['town_of_birth'].str.title()


# ====================== ENTITY CLASS =========================
class EntityProcessor(SanctionsProcessor):
    designation_type = 'Entity'
    output_path = 'entity_sanctions.csv'
    output_cols = [
        'type_of_entity', 'parent_company', 'subsidiaries', 'business_registration_number_(s)',
        # CHECK WHATS NEEDED AND NOT
        'unique_id','ofsi_group_id', 'primary_name', 'aliases',
        'date_of_birth','nationality','gender','town_of_birth','country_of_birth',
        'phone_number','email_address', 'national_identifier_number','passport_number',
        'address','address_postal_code','address_country',
        'regime_name','designation_source','date_designated','sanctions_imposed',
        'position','last_updated'
    ]



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Run in this format: python processor.py {path_to_csv}')
        sys.exit(1)

    # clean = Processer(sys.argv[1])
    # clean.run()