# How to run script to clean sanctions list data
- Clone the repository and enter the directory
- From the root of the directory, install the requirements
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
- Very messy dataset, essentially a cartesian product of data for every ID, no duplicate records

- Filtered to only extract individuals from the UK sanction list, since we're dealing with customer information, 'Ship' and 'Entity' designations were ignored
    - 3977 Individuals, 1569 Entities, 631 Ships
        - Missing values out of 3977 individuals
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

- Multiple records contain multiple possible dates of birth, often with incomplete date components, e.g., dd/mm/1975

- National Identifier Number & Passport Number:
    - Some fields are have inconsistencies/entry error, e.g., ['Indonesia number 1608600001', Russian number 0258399], can be fixed by stripping characters or regex matching, but can risk of deleting actual data such as TR024417

- Date of Birth
    - Many entries has missing values, e.g., missing day/month dd/mm/1975
    - Also many have multiple 'possible' birth years
    - Converting to date dtype can break

## Transformations
- Name fields:
    <!-- - % of missing names -->
    - Formatting inconsistency (some uppercased/lowercased, whitespace preceding/following)
    - Modified to one 'primary_name' field in order of First Name, Other/Middle Names, Surname, for Primary Names
- Aliases:
    - Multiple aliases/name variation under a Primary Name, concatenated into 'aliases' field for each unique_id and name
- Date of Birth
    - Kept raw data but concatenated (for multiple) into one string 'date_of_birth' field
- Address Fields:
    - Kept raw and concatenated into one 'address' field

## Formatting
- Column Names:
    - Standardised to lowercasing, replace whitespace and '-' as underscore
- Dates (last_updated, date_designated)
    - Converted columns 'last_updated' and 'date_designated' data type to datetime
- OFSI Group ID
    - Originally floats, converted to 'Int64' (which allows null values, could also leave as is)



Missing or inconsistent fields

Duplicate records 

Formatting inconsistencies 

Any other observations