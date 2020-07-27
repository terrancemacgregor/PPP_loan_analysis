"""
The purpose of this program is to enable the simple analysis of companies that utilized the
Paycheck Protection Program (PPP).  The PPP is an SBA loan that helps businesses keep their
workforce employed during the Coronavirus (COVID-19) crisis. Ref:
https://www.sba.gov/funding-programs/loans/coronavirus-relief-options/paycheck-protection-program
"""
import csv
import collections
from os import path
import urllib.request
import time
import argparse


# Source files, please see README.md for more details on each file.
# ppp csv
PATH_PPP_SOURCE_FILE = './input_files/foia_150k_plus.csv'
S3_PPP_SOURCE = 'https://s3.amazonaws.com/ppp.sba.gov/foia_150k_plus.csv'

# This section is dedicated to loading the NAICS codes for a simple human translations.
# The file came from: https://www.census.gov/eos/www/naics/downloadables/downloadables.html
NAICS_CODES_HUMAN_DICT = {}
PATH_TO_NAICS_SOURCE_FILE = './input_files/2017_NAICS_Structure.csv'
S3_NAICS_SOURCE_FILE = 'https://s3.amazonaws.com/ppp.sba.gov/2017_NAICS_Structure.csv'

def naics_csv_prep():
    """
    # The purpose of this function is to download the ppp source file from s3 automatically.
    :return:
    """
    start = time.time()

    if not path.exists(PATH_TO_NAICS_SOURCE_FILE):
        print("NAICS - The NAICS source file wasn't found in your local directory system.")
        print("NAICS - Downloading the csv file from Amazon's S3 file storage: " +
              S3_NAICS_SOURCE_FILE)

        with urllib.request.urlopen(S3_NAICS_SOURCE_FILE) as naics_file, \
                open(PATH_TO_NAICS_SOURCE_FILE, 'w') as file_output:
            file_output.write(naics_file.read().decode())
    else:
        print("NAICS - Found the naics source csv")

    with open(PATH_TO_NAICS_SOURCE_FILE, newline='') as csvfile:
        foia_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        print("NAICS - processing NAICS Code data")
        for row in foia_reader:
            NAICS_CODES_HUMAN_DICT[row[0]] = row[1]

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print("NAICS Done with initial processing of naics code in " + str(elapsed))

    return True


# 0 LoanRange
# 1 BusinessName
# 2 Address
# 3 City
# 4 State
# 5 Zip
# 6 NAICSCode
# 7 BusinessType
# 8 RaceEthnicity
# 9 Gender
# 10 veteran
# 11 NonProfit
# 12 JobsRetained
# 13 DateApproved
# 14 Lender
# 15 CD


##############################################################

def write_csv_out(csv_name, array_input):
    """
    # These are a series of filters that you can run.  Not, the input from each one
    # goes into the output of each one if you want to combine filters.
    :param csv_name:
    :param array_input: CSV values to write out.
    :return: True by default
    """
    timestr = time.strftime("%Y%m%d-%H%M%S")
    csv_name = timestr + "_" + csv_name

    header_row = ["BusinessName", "Address", "City", "State", "Zip Code", "NAICSCode", "NAICSHuman",
                  "BusinessType",
                  "RaceEthnicity",
                  "Gender", "veteran", "NonProfit", "JobsRetained", "DateApproved", "Lender",
                  "CD", "LoanRange",
                  "average_loan_range"]
    with open('./output_files/' + csv_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(header_row)
        for item in array_input:
            csv_writer.writerow(item)
    print("Done writing to " + csv_name)
    return True


def ppp_csv_prep():
    """
    The purpose of this function is to download the ppp source file from s3 automatically.
    :return: True by default
    """
    start = time.time()
    if not path.exists(PATH_PPP_SOURCE_FILE):
        print("PPP source file wasn't found in your local directory system.")
        print("Downloading the csv file from Amazon's S3 file storage: " + S3_PPP_SOURCE)
        print("Note, this is a large file and will take a few seconds to complete")
        with urllib.request.urlopen(S3_PPP_SOURCE) as testfile, \
                open(PATH_PPP_SOURCE_FILE, 'w') as file_output:
            file_output.write(testfile.read().decode())
    else:
        print("Found the ppp source csv")

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print("PPP Done downloading CSV in " + str(elapsed))

    return True

def process_ppp_data():
    """
    This function serves as a basic ETL (extract, translate, load function).  In addition to loading
    the data, some enrichments are made. The enrichments to the data are:
    1. Human readable names to NAICS codes
    2. Average for the a loan range. This isn't accurate, but better than a range.
    :return: result set.
    """

    print("PPP Reading in csv data")
    start = time.time()
    results = []
    ppp_csv_prep()
    naics_csv_prep()

    with open(PATH_PPP_SOURCE_FILE, newline='') as csvfile:
        foia_reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in foia_reader:
            loan_range = row[0]
            business_name = row[1]
            address = row[2]
            city = row[3]
            state = row[4]
            zip_code = row[5]
            naics_code = row[6]
            business_type = row[7]
            race_ethnicity = row[8]
            gender = row[9]
            veteran = row[10]
            non_profit = row[11]
            jobs_retained = row[12]
            date_approved = row[13]
            lender = row[14]
            cd_field = row[15]

            try:
                naics_human = NAICS_CODES_HUMAN_DICT[naics_code]

            except Exception:
                naics_human = "tbd"

            average_loan_range = None

            if "$150,000-350,000" in loan_range:
                average_loan_range = 250000.00
            elif "$350,000-1 million" in loan_range:
                average_loan_range = 675000.00
            elif "$1-2 million" in loan_range:
                average_loan_range = 1500000.00
            elif "$2-5 million" in loan_range:
                average_loan_range = 3500000.00
            elif "$5-10 million" in loan_range:
                average_loan_range = 7500000.00

            array = [business_name, address, city, state, zip_code, naics_code, naics_human,
                     business_type, race_ethnicity, gender, veteran, non_profit, jobs_retained,
                     date_approved, lender, cd_field, loan_range, average_loan_range]

            results.append(array)

    end = time.time()
    elapsed = time.strftime("%H:%M:%S", time.gmtime(end - start))
    print("PPP Done with initial processing of csv  " + str(elapsed))

    return results



def get_report_unique_naics(highest_values, input_array_ppp_requests):
    """ This returns a complex Counter collections if needed."""
    cnt = collections.Counter()
    for item in input_array_ppp_requests:
        cnt[item[5]] += 1

    for item in cnt.most_common(highest_values):
        print(item)

    return cnt

def get_company_ppp_requests_filter(field_name, search_term_array, input_array_ppp_requests):
    """
    This is an important function that lets us filter.
    It implies that you know the actual number in the array, which needs to be refactored out.
    """
    print("Filtering based on " + str(search_term_array))
    ppp_company_request_results = []
    for company in input_array_ppp_requests:
        for search_term in search_term_array:
            if search_term in str(company[field_name]).lower():
                ppp_company_request_results.append(company)
                # print ("We found " + search_term + " in " + str(company[field_name]).lower() +
                # " " + str(company))
                break
    return ppp_company_request_results


def get_total_value(input_array_ppp_requests):
    """
    This is a simple way to get the total of a results set.
    :param input_array_ppp_requests:
    :return: total dollar amounts
    """
    total_dollars_average = 0
    for ppp in input_array_ppp_requests:
        total_dollars_average = total_dollars_average + ppp[-1]
    total_dollars_average = "${:,.2f}".format(total_dollars_average)
    return total_dollars_average


def main():
    """
    This is the main function that is used to kick off the analysis.
    :return:
    """
    parser = argparse.ArgumentParser(description='Search FOIA PPP account requests.  '
                                                 'Utilized NAICS (pronounced NAKES) '
                                                 'Code for the classification of US businesses.')
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Verbose", action="store_true")
    parser.add_argument("-state", nargs='+', help="Enter 2 digit state codes, e.g. \'NY CT DC\'")
    parser.add_argument("-name", nargs='+',
                        help="You can search with a single word for company name. Eg Smith Company")

    # naics_codes_help_text = "A NAICS (pronounced NAKES) Code is a classification scheme for US " \
    #                        "businesses."

    parser.add_argument("-naics_code", nargs='+', help="Enter naics codes like: '541511'.")

    parser.add_argument("-naics_human", nargs='+',
                        help="Enter a human readable string e.g.Programming Services.")

    args = parser.parse_args()

    # Load our initial data set.
    results = process_ppp_data()
    print("Main - Running Query Set")
    print("Main - Our initial data set = " + str(len(results)) + " ppp loans")
    print("#######################################")
    print("Main - Filtering by state with this many input records " + str(len(results)))
    print("Main - The value we have for state is:" + str(args.state))

    if args.state:

        lower_case_states = []
        for state in args.state:
            lower_case_states.append(state.lower())
        print("State Filter - Processing " + str(lower_case_states))

        results = get_company_ppp_requests_filter(3, lower_case_states, results)
        print("State Filter - Our post State filters = " + str(len(results)) + " ppp loans")

    print("Main - Filtering by company with this many input records " + str(len(results)))

    if args.name:
        lower_case_names = []
        for name in args.name:
            lower_case_names.append(name.lower())

        print("Processing " + str(lower_case_names))
        results = get_company_ppp_requests_filter(0, lower_case_names, results)
        print("Company Name Filter - Our post company name filters = " + str(
            len(results)) + " ppp loans")

    if args.naics_code:
        results = get_company_ppp_requests_filter(4, args.naics_code, results)
        print(
            "NAICS Code Filter - Our post naics_code filter = " + str(len(results)) + " ppp loans")

    if args.naics_human:

        lower_case_human_search = []
        for search_term in args.naics_human:
            lower_case_human_search.append(search_term.lower())

        results = get_company_ppp_requests_filter(5, lower_case_human_search, results)
        print("NAICS Human Filter - Our post naics_search_term filter = " + str(
            len(results)) + " ppp loans")

    print("Main - Done with the query results.  Writing output to file")
    write_csv_out("query_results.csv", results)

    if args.verbose:
        for ppp_loan in results:
            print("MAIN Results " + str(ppp_loan))

        get_report_unique_naics(20, results)


if __name__ == "__main__":
    main()
