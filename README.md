clone,

requirements
pip install -r requirements.txt

run main




## Findings
- Very messy dataset, essentially a cartesian product of data for every ID

- Filtered to only extract individuals from the UK sanction list, since we're dealing with customer information, 'Ship' and 'Entity' designations were ignored

- Several records contain multiple possible dates of birth, often with incomplete date components

- National Identifier Number & Passport Number:
    - Some fields are have inconsistencies/entry error, e.g., ['Indonesianumber1608600001', Russiannumber0258399], can be fixed by stripping characters or regex matching, but can risk of deleting actual data

- Date of Birth
    - Many entries has missing values, e.g., missing day/month dd/mm/1975
    - Also many have multiple 'possible' birth years
    - Converting to date dtype can break


Missing or inconsistent fields

Duplicate records 

Formatting inconsistencies 

Any other observations

# Transformations
- Column Names:
    - Standardised to lowercasing and underscore as whitespace
- Dates (last_updated)
    - Converted data type to DATE/TIME
- Name fields:
    <!-- - % of missing names -->
    - Formatting inconsistency (some uppercased/lowercased, whitespace preceding/following)
    - Modified to one field in order of First Name, Other/Middle Names, Surname
- Address Fields:
    <!-- - % of missing addresses -->


