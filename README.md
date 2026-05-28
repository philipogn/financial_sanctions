# How to run script to clean sanctions list data
- Clone the repository and enter the directory
- From the root of the directory, install the requirements (only require pandas and numpy)
```sh
pip install -r requirements.txt
```
- Run the processor file with path (e.g., python processor.py data/UK-Sanctions-List.csv)
```sh
python processor.py {path_to_dataset}
```
- It will then output into a CSV file 'individual_sanctions.csv'


# Data Quality Assessment
## Findings
- Very messy dataset, essentially a cartesian product of data for every ID, no duplicate records.

- 6177 Unique ID's, where designation types are 3977 Individuals, 1569 Entities, 631 Ships.
    - Missing values out of 3977 individuals
        - 127 ofsi_group_id
        - 669 date_of_birth
        - 1110 nationality
        - 1502 country_of_birth
        - 3905 phone_number
        - 3922 email_address
        - 3578 national_identifier_number
        - 3398 passport_number
        - 2450 address
        - 3138 address_postal_code
        - 2134 address_country

- Phone Numbers
    - Inconsistent and some seems partial, some have international access code, dash and/or bracket formatted, some don't.
    - A few include multiple numbers in one field (e.g., '9562236 (08 Apr 2010-) 74955098211 (29 Aug 2007-) 5098211 (14 Jun 2006-)'), probably ideal in this scenario to manually format, as automating can cause potential errors if new/updated dataset is being processed.
    - Mostly kept raw, only removed whitespace, and leading apostrophe (due to Excels text-forcing convention https://support.microsoft.com/en-gb/office/format-numbers-as-text-583160db-936b-4e52-bdff-6f1863518ba4).

- National Identifier Number & Passport Number:
    - Some fields have inconsistencies/entry error, e.g., ['Indonesia number 1608600001', Russian number 0258399], can be fixed by stripping characters or regex matching, but can risk of deleting actual data such as TR024417.

- Date of Birth
    - Multiple records contain multiple 'possibly known' dates of birth, often with incomplete date components, e.g., missing day/month, dd/mm/1975.
    - Converting to datetime can lose partial dates, so it's kept as a string.


## Transformations
- Filtered to only extract individuals from the UK sanction list, since we're dealing with customer information, 'Ship' and 'Entity' designations were ignored.

- Name Types included ['Primary Name', 'Alias', 'Primary Name Variation', 'Primary name', 'ALias', 'Primary name variation'], inconsistent formatting, so these were standardised for processing name fields below.

- Name fields:
    - Formatting inconsistency (some uppercased/lowercased, whitespace preceding/following)
    - Modified to one 'primary_name' field, capitalised in order of First Name (Name 1), Other/Middle Names (Name 2-5), Surname (Name 6), for Primary Names.

- Aliases:
    - Multiple aliases/name variation under a Primary Name, concatenated into 'aliases' field for each unique_id and name.

- Date of Birth
    - Kept raw data but concatenated (for multiple) into one string 'date_of_birth' field.

- Address Fields:
    - Kept raw and concatenated into one 'address' field.

## Formatting
- Column Names:
    - Standardised to lowercasing, replace whitespace and '-' as underscore
- Dates (last_updated, date_designated).
    - Converted columns 'last_updated' and 'date_designated' data type to datetime.
- OFSI Group ID
    - Originally floats, converted to 'Int64' (which allows null values, could also leave as is).
- Gender
    - Included ['Female','female','Male','male'], inconsistent casing standardised to capitalisation.

# Output Details
- Resulting columns
    - ['unique_id', 'ofsi_group_id', 'primary_name', 'aliases', 'date_of_birth', 'nationality','gender', 'town_of_birth', 'country_of_birth', 'phone_number', 'email_address', 'national_identifier_number', 'passport_number', 'address', 'address_postal_code', 'address_country', 'regime_name', 'designation_source', 'date_designated', 'sanctions_imposed',  'position', 'last_updated', ]
- 3977 rows of data