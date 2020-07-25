# PPP Loan Analysis

## PPP Company loan analysis based on FIOA requests.  

The purpose of this program is to enable the simple analysis of companies that utilized the Paycheck Protection Program (PPP).  The PPP is an SBA loan that helps businesses keep their 
workforce employed during the Coronavirus (COVID-19) crisis.
Ref:  [https://www.sba.gov/funding-programs/loans/coronavirus-relief-options/paycheck-protection-program](https://sba.box.com/s/wz72fqag1nd99kj3t9xlq49deoop6gzf)

This project is intended to provide transarency into what is one of the largest government loan programs ever initiated by the US government.  By providing transparency into where the money has gone, we have a chance to better respond to scenrios like this.  Additionally, we have a tool that can be used in the future to help identify were loans have been paid back, where loans were forgiven, and unfortunately, were fraud took place.  


## Source FOIA File from the US Government

### Source is here:
Website: [https://home.treasury.gov/policy-issues/cares-act/assistance-for-small-businesses/sba-paycheck-protection-program-loan-level-data](https://sba.box.com/s/wz72fqag1nd99kj3t9xlq49deoop6gzf)
### File Link
File: [https://sba.box.com/s/wz72fqag1nd99kj3t9xlq49deoop6gzf](https://sba.box.com/s/wz72fqag1nd99kj3t9xlq49deoop6gzf)
### Amazon S3 Location
CSV: [https://s3.amazonaws.com/ppp.sba.gov/foia_150k_plus.csv](https://s3.amazonaws.com/ppp.sba.gov/foia_150k_plus.csv)
Note, the file size is too large to commit to github without using their large file size. The file was moved to use Amazon's s3 file storage system.
This program checks your local file system to see if it is there.  If it isn't, it is downloaded automatically.

## NAICS Coder
We used the NAICS Codes from 2017 to decode the company classification codes that are part of the categorization used by the SBA to identify what type of company received the funds.  
Website [https://www.census.gov/eos/www/naics/downloadables/downloadables.html](https://www.census.gov/eos/www/naics/downloadables/downloadables.html)

### File Link
File: [https://www.census.gov/eos/www/naics/2017NAICS/2017_NAICS_Structure.xlsx](https://www.census.gov/eos/www/naics/2017NAICS/2017_NAICS_Structure.xlsx)

Note, some basic edits were made to convert the xlsx file into a csv.  Those edits were primarily to remove the first few rows.

## How to Run
Using Python interpreter 3.6
<pre>
usage: ppp_analysis.py [-h] [-v] [-state STATE [STATE ...]]
                       [-name NAME [NAME ...]]
                       [-naics_code NAICS_CODE [NAICS_CODE ...]]
                       [-naics_human NAICS_HUMAN [NAICS_HUMAN ...]]
optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbose
  -state STATE [STATE ...]
                        Enter 2 digit state codes, e.g. 'NY CT DC'
  -name NAME [NAME ...]
                        You can search with a single word for company name.
                        E.g Smith Company
  -naics_code NAICS_CODE [NAICS_CODE ...]
                        Enter naics codes like: '541511 5416'. 541511 = Custom
                        Computer Programming Services.
  -naics_human NAICS_HUMAN [NAICS_HUMAN ...]
                        Enter a human readable string e.g.Programming
                        Services.
</pre>

### To Query Multiple States, Company Name, NAICS Code
> python ppp_analysis.py -v -state md ct dc -name Johnson -naics_code 541330

<pre>Main - Filtering by state with this many input records 661219
Main - The value we have for state is:['md', 'ct', 'dc']
State Filter - Processing ['md', 'ct', 'dc']
Filtering based on ['md', 'ct', 'dc']
State Filter - Our post State filters = 24320 ppp loans
Main - Filtering by company with this many input records 24320
Processing ['johnson']
Filtering based on ['johnson']
Company Name Filter - Our post company name filters = 22 ppp loans
Filtering based on ['541330']
NAICS Code Filter - Our post naics_code filter = 1 ppp loans
Main - Done with the query results.  Writing output to file
Done writing to 20200725-084106_query_results.csv
MAIN Results ['CHARLES P JOHNSON & ASSOC., INC.', '1751 Elton Road #300', 'SILVER SPRING', 'MD', '541330', 'Engineering Services', 'Corporation', 'Unanswered', 'Unanswered', 'Unanswered', '', '90', '04/13/2020', 'Sandy Spring Bank', 'MD - 03', 'c $1-2 million', 1500000.0]
('Engineering Services', 1)
</pre>

This tells us that we are have 1 company that has the name johnson in it across multiple states (md, ct, dc) that has the NAICS code of 541330

## Output
The output is a CSV with these column headers.
<pre>
"BusinessName",
"Address"
"City"
"State"
"NAICSCode"
"NAICSHuman"
"BusinessType"
"RaceEthnicity"
"Gender"
"Veteran"
"NonProfit"
"JobsRetained"
"DateApproved"
"Lender"
"CD"
"LoanRange"
"averageLoanRange"</pre>