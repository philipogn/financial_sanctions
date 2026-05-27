clone,

requirements
pip install -r requirements.txt

run main




## Findings
- Very messy dataset, essentially a cartesian product of data for every ID

- Filtered to only extract individuals from the UK sanction list, since we're dealing with customer information, 'Ship' and 'Entity' designations were ignored
    - 3977 Individuals
    - 1569 Entities
    - 631 Ships

- Multiple records contain multiple possible dates of birth, often with incomplete date components, e.g., dd/mm/1975

- National Identifier Number & Passport Number:
    - Some fields are have inconsistencies/entry error, e.g., ['Indonesia number 1608600001', Russian number 0258399], can be fixed by stripping characters or regex matching, but can risk of deleting actual data

- Date of Birth
    - Many entries has missing values, e.g., missing day/month dd/mm/1975
    - Also many have multiple 'possible' birth years
    - Converting to date dtype can break


Missing or inconsistent fields

Duplicate records 

Formatting inconsistencies 

Any other observations

# Transformations
- Name fields:
    <!-- - % of missing names -->
    - Formatting inconsistency (some uppercased/lowercased, whitespace preceding/following)
    - Modified to one 'full_name' field in order of First Name, Other/Middle Names, Surname
- Aliases:
    - Multiple aliases under a Primary Name, concatenated into 'aliases' field for each unique_id and name
- Date of Birth
    - Kept raw data but concatenated (for multiple) into one string 'date_of_birth' field
- Address Fields:
    - Kept raw and concatenated into one 'address' field

# Formatting
- Column Names:
    - Standardised to lowercasing, replace whitespace and '-' as underscore
- Dates (last_updated, date_designated)
    - Converted columns 'last_updated' and 'date_designated' data type to datetime
- OFSI Group ID
    - Originally floats, converted to 'Int64' (which allows null values, could also leave as is)