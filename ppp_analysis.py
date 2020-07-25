import csv
import collections
from os import path
import urllib.request
import time

""" The purpose of this program is to enable the simple analysis of companies that utilized the 
Paycheck Protection Program (PPP).  The PPP is an SBA loan that helps businesses keep their 
workforce employed during the Coronavirus (COVID-19) crisis.
Ref:  https://www.sba.gov/funding-programs/loans/coronavirus-relief-options/paycheck-protection-program
"""


# Source files, please see README.md for more details on each file.
# ppp csv
path_ppp_source_file = './input_files/foia_150k_plus.csv'
s3_ppp_source = 'https://s3.amazonaws.com/ppp.sba.gov/foia_150k_plus.csv'

# This section is dedicated to loading the NAICS codes for a simple human translations.
# The file came from: https://www.census.gov/eos/www/naics/downloadables/downloadables.html
naics_codes_human_dict = {}
path_to_naics_source_file = './input_files/2017_NAICS_Structure.csv'
s3_naics_source_file = 'https://s3.amazonaws.com/ppp.sba.gov/2017_NAICS_Structure.csv'

# The purpose of this function is to download the ppp source file from s3 automatically.
def naics_csv_prep():
    start = time.time()

    if path.exists(path_to_naics_source_file) == False:
        print("NAICS - The NAICS source file wasn't found in your local directory system.")
        print("NAICS - Downloading the csv file from Amazon's S3 file storage: " + s3_naics_source_file)

        with urllib.request.urlopen(s3_naics_source_file) as naics_file, open( path_to_naics_source_file, 'w') as f:
            f.write(naics_file.read().decode())
    else:
        print("NAICS - Found the naics source csv")

    with open(path_to_naics_source_file, newline='') as csvfile:
        foia_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        print("NAICS - processing NAICS Code data")
        for row in foia_reader:
            naics_codes_human_dict[row[0]] = row[1]

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print ("NAICS Done with initial processing of naics code in " + str(elapsed))


#0 LoanRange
#1 BusinessName
#2 Address
#3 City
#4 State
#5 Zip
#6 NAICSCode
#7 BusinessType
#8 RaceEthnicity
#9 Gender
#10 Veteran
#11 NonProfit
#12 JobsRetained
#13 DateApproved
#14 Lender
#15 CD



##############################################################

# These are a series of filters that you can run.  Not, the input from each one
# goes into the output of each one if you want to combine filters.

def write_csv_out(csvName, array_input):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    csvName = timestr + "_" +csvName

    header_row = ["BusinessName", "Address", "City", "State", "NAICSCode", "NAICSHuman", "BusinessType", "RaceEthnicity",
             "Gender", "Veteran", "NonProfit", "JobsRetained", "DateApproved", "Lender", "CD", "LoanRange",
             "averageLoanRange"]

    with open('./output_files/'+csvName, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(header_row)
        for item in array_input:
            csv_writer.writerow(item)
    print ("Done writing to " + csvName)

# The purpose of this function is to download the ppp source file from s3 automatically.
def ppp_csv_prep():

    start = time.time()
    if path.exists(path_ppp_source_file) == False:
        print("PPP source file wasn't found in your local directory system.")
        print ("Downloading the csv file from Amazon's S3 file storage: " + s3_ppp_source)
        print ("Note, this is a large file and will take a few seconds to complete")
        with urllib.request.urlopen(s3_ppp_source) as testfile, open(path_ppp_source_file, 'w') as f:
            f.write(testfile.read().decode())
    else:
        print ("Found the ppp source csv")

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print ("PPP Done downloading CSV in " + str(elapsed))


# This is the basic structure to read in data and conduct some basic data enrichments.
# The enrichments to the data are:
# 1. Human readable names to NAICS codes
# 2. Average for the a loan range. This isn't accurate, but better than a range.

def processPPPData ():

    print ("PPP Reading in csv data")
    start = time.time()
    results = []
    ppp_csv_prep()
    naics_csv_prep()

    with open(path_ppp_source_file, newline='') as csvfile:
        foia_reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in foia_reader:
                LoanRange = row[0]
                BusinessName = row[1]
                Address = row[2]
                City = row[3]
                State = row[4]
                Zip = row[5]
                NAICSCode = row[6]
                BusinessType = row[7]
                RaceEthnicity = row[8]
                Gender = row[9]
                Veteran = row[10]
                NonProfit = row[11]
                JobsRetained = row[12]
                DateApproved = row[13]
                Lender = row[14]
                CD = row[15]

                try:
                    NAICSHuman = naics_codes_human_dict[NAICSCode]

                except:
                    NAICSHuman = "tbd"
                averageLoanRange =0;

                if "$150,000-350,000" in LoanRange:
                    averageLoanRange = 250000.00
                elif "$350,000-1 million" in LoanRange:
                    averageLoanRange = 675000.00
                elif "$1-2 million" in LoanRange:
                    averageLoanRange = 1500000.00
                elif "$2-5 million" in LoanRange:
                    averageLoanRange = 3500000.00
                elif "$5-10 million" in LoanRange:
                    averageLoanRange = 7500000.00
                else:
                    averageLoanRange = 0.00

                array = [BusinessName, Address, City, State, NAICSCode, NAICSHuman, BusinessType, RaceEthnicity,Gender,Veteran,NonProfit,JobsRetained,DateApproved,Lender,CD, LoanRange,averageLoanRange ]
                results.append(array)

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print ("PPP Done with initial processing of csv  " + str(elapsed))

    return results

# This returns a complex Counter collections if needed.
# highestValues
def getReportUniqueNaics(highestValues, input_array_ppp_requests):
    cnt = collections.Counter()
    for item in input_array_ppp_requests:
        cnt[item[5]] += 1

    for item in cnt.most_common(highestValues):
        print (item)

    return cnt

# This is an important function that lets us filter.
# It implies that you know the actual number in the array, which needs to be refactored out.
def getCompanyPPPRequestsFilter(field_name, search_term_array, input_array_ppp_requests):

    print ("Filtering based on "+ str(search_term_array))
    ppp_company_request_results = []
    for company in input_array_ppp_requests:
        for search_term in search_term_array:
            if search_term in str(company[field_name]).lower():
                ppp_company_request_results.append(company)
                #print ("We found " + search_term + " in " + str(company[field_name]).lower() + " " + str(company))
                break
    return ppp_company_request_results

def get_total_value(input_array_ppp_requests):
    total_dollars_average = 0
    for ppp in input_array_ppp_requests:
        total_dollars_average = total_dollars_average + ppp[-1]
    total_dollars_average = "${:,.2f}".format(total_dollars_average)
    return total_dollars_average

import argparse

def main():

    parser = argparse.ArgumentParser(description='Search FOIA PPP account requests.  Utilized NAICS (pronounced NAKES) '
                                                 'Code for the classification of US businesses.')
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose", help="Verbose", action="store_true")
    parser.add_argument("-state",  nargs='+', help="Enter 2 digit state codes, e.g. \'NY CT DC\'" )
    parser.add_argument("-name", nargs ='+', help="You can search with a single word for company name. E.g Smith Company")

    naics_codes_help_text = "A NAICS (pronounced NAKES) Code is a classification scheme for US businesses."
    parser.add_argument("-naics_code", nargs='+', help="Enter naics codes like: \'541511 5416\'. "
                                            " 541511 = Custom Computer Programming Services. ")
    parser.add_argument("-naics_human", nargs='+', help="Enter a human readable string e.g.Programming Services." )

    args = parser.parse_args()

    # Load our initial data set.
    results = processPPPData()
    print ("Main - Running Query Set")
    print ("Main - Our initial data set = " + str(len(results)) + " ppp loans")
    print ("#######################################")
    print ("Main - Filtering by state with this many input records "+ str(len(results)))
    print ("Main - The value we have for state is:" + str(args.state))

    if args.state:

        lower_case_states = []
        for state in args.state:
            lower_case_states.append(state.lower())
        print("State Filter - Processing "+ str(lower_case_states))

        results = getCompanyPPPRequestsFilter(3, lower_case_states, results);
        print("State Filter - Our post State filters = " + str(len(results)) + " ppp loans")

    print ("Main - Filtering by company with this many input records "+ str(len(results)))

    if args.name:
        search_terms = str(args.name).lower()
        lower_case_names =[]
        for name in args.name:
            lower_case_names.append(name.lower())

        print("Processing "+ str(lower_case_names))
        results = getCompanyPPPRequestsFilter(0, lower_case_names, results);
        print("Company Name Filter - Our post company name filters = " + str(len(results)) + " ppp loans")

    if args.naics_code:

        results = getCompanyPPPRequestsFilter(4, args.naics_code, results);
        print("NAICS Code Filter - Our post naics_code filter = " + str(len(results)) + " ppp loans")

    if args.naics_human:

        lower_case_human_search =[]
        for search_term in args.naics_human:
            lower_case_human_search.append(search_term.lower())

        results = getCompanyPPPRequestsFilter(5, lower_case_human_search, results);
        print("NAICS Human Filter - Our post naics_search_term filter = " + str(len(results)) + " ppp loans")

    print ("Main - Done with the query results.  Writing output to file")
    write_csv_out("query_results.csv", results)

    if args.verbose:
        for ppp_loan in results:
            print ("MAIN Results " + str(ppp_loan))

        uniqueReport = getReportUniqueNaics(20,results);

if __name__ == "__main__":
    main()