#Import all the required libraries
import glob
import os
import pandas as pd
import numpy as np

#Console Settings
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# Specify the folders containing the CSV files and directory
current_directory = os.getcwd()
net_suite_directory = '/assignment_1/netsuite_data_for_specific_area'
settlements_directory = '/assignment_1/jb-dea-test-assignment-main/settlement'
settlement_path = current_directory + settlements_directory
net_suite_path = current_directory + net_suite_directory

# Use glob to get all the settlements and NetSuit CSV files  in the folder
settlement_csv = glob.glob(os.path.join(settlement_path, "*.csv"))
df_settlements = pd.concat([pd.read_csv(file,sep=";") for file in settlement_csv], ignore_index=True)
netsuite_csv = glob.glob(os.path.join(net_suite_path, "*.csv"))
df_netsuite = pd.concat([pd.read_csv(file) for file in netsuite_csv], ignore_index=True)

df_all_netsuite_data_wo_constrainAUSD = pd.read_csv('assignment_1/netsuite_with_out_constrains_AUSD.csv', low_memory=False)
df_all_netsuite_data_wo_constrain_GBP = pd.read_csv('assignment_1/netsuite_without_constrains_GBP.csv', low_memory=False)


#%%
## Create empty list to save required outputs.
missing_in_ns = []       ## The transaction available in settlement but missing in netsuite
missing_in_sett = []     ## The transaction available in settlement but missing in netsuite
list_off_missmathc = []  ## The transaction available in settlement and netsuite but the amounts are not matching.

list_of_all_the_merchant_accounts = list(df_settlements.MERCHANT_ACCOUNT.unique())
list_of_all_the_batch_number = list(df_settlements.BATCH_NUMBER.unique())
list_of_all_the_batch_number = sorted(list_of_all_the_batch_number)


def checker(merchant_account,batch_number):
    ## Filter the merchant account in both settlement and netsuite
    df_sett = df_settlements[df_settlements.MERCHANT_ACCOUNT == merchant_account]
    df_ns = df_netsuite[df_netsuite.MERCHANT_ACCOUNT == merchant_account]

    ## Filter the batch_number in both settlement and netsuite.
    df_sett = df_sett[df_sett.BATCH_NUMBER == batch_number]
    df_ns = df_ns[df_ns.BATCH_NUMBER == batch_number]

    # Prepare pivot tables by aggregating the 'GROSS' values for settlement data and 'AMOUNT_FOREIGN' values for
    # Netsuite data, grouped by 'ORDER_REF'. If either the Netsuite or settlement dataset is empty, create an
    # empty DataFrame with matching columns to ensure compatibility.
    if df_sett.empty:
        df_sett_pivot = pd.DataFrame(columns=['ORDER_REF', 'GROSS','sum'])  # Define columns as per your requirement
        #print("df_sett is empty. Created an empty df_sett_pivot.")
    else:
        df_sett_pivot = pd.pivot_table(df_sett, values='GROSS', index='ORDER_REF', aggfunc='sum').reset_index()
    if df_ns.empty:
        df_ns_pivot = pd.DataFrame(columns=['ORDER_REF', 'AMOUNT_FOREIGN'])  # Define columns as per your requirement
        #print("df_ns is empty. Created an empty df_ns_pivot.")
    else:
        df_ns_pivot = pd.pivot_table(df_ns, values='AMOUNT_FOREIGN', index='ORDER_REF', aggfunc='sum').reset_index()

    ## Duplicate the Order_Reff column which I will use to make index
    df_sett_pivot['ORDER_REF_index'] = df_sett_pivot['ORDER_REF']
    df_ns_pivot['ORDER_REF_index'] = df_ns_pivot['ORDER_REF']

    ## Set the Order_REF column as index
    df_sett_pivot.set_index('ORDER_REF_index', inplace=True)
    df_ns_pivot.set_index('ORDER_REF_index', inplace=True)

    ## Assign sum of Gross from settlement to Netsuite & Sum of Amount_Foreing from Netsuite to Setllement
    df_sett_pivot['Total_in_netsuite'] = df_sett_pivot['ORDER_REF'].map(df_ns_pivot['AMOUNT_FOREIGN']).fillna(
        'Not_Available')
    df_ns_pivot['Total_in_settlement'] = df_ns_pivot['ORDER_REF'].map(df_sett_pivot['GROSS']).fillna('Not_Available')

    ## Excluding the missmatch between settlement and Netsuite
    available_in_sett_missing_in_ns = df_sett_pivot[df_sett_pivot['Total_in_netsuite'] == 'Not_Available']
    available_in_netsuite_missing_in_sett = df_ns_pivot[df_ns_pivot['Total_in_settlement'] == 'Not_Available']

    ## Append the missmatch data to list missing_in_ns
    available_in_netsuite_missing_in_sett['merchant_account'] = merchant_account
    available_in_netsuite_missing_in_sett['batch_number'] = batch_number
    missing_in_ns.append(available_in_sett_missing_in_ns)

    ## Append the missmatch data to list missing_in_sett
    available_in_sett_missing_in_ns['merchant_account'] = merchant_account
    available_in_sett_missing_in_ns['batch_number'] = batch_number
    missing_in_sett.append(available_in_netsuite_missing_in_sett)

    ## Filter the matches and continue investigation
    df_sett_pivot = df_sett_pivot[df_sett_pivot['Total_in_netsuite'] != 'Not_Available']
    df_ns_pivot = df_ns_pivot[df_ns_pivot['Total_in_settlement'] != 'Not_Available']

    ## Compare the Settlement and NetSuite Sum
    df_sett_pivot['Comparison'] = df_sett_pivot['Total_in_netsuite'] == df_sett_pivot['GROSS']
    df_ns_pivot['Comparison'] = df_ns_pivot['Total_in_settlement'] == df_ns_pivot['AMOUNT_FOREIGN']

    ## Filter the ones which values are not mathcing and append the mismatch Order_REF to a list
    df_sett_pivot_missmatch = df_sett_pivot[df_sett_pivot.Comparison == False]
    mismatch_list_sett = list(df_sett_pivot_missmatch['ORDER_REF'])
    filtered_mismatch_sett = df_sett_pivot[df_sett_pivot['ORDER_REF'].isin(mismatch_list_sett)]
    df_ns_pivot_missmatch = df_ns_pivot[df_ns_pivot.Comparison == False]
    mismatch_list_ns = list(df_ns_pivot_missmatch['ORDER_REF'])
    filtered_mismatch_ns = df_ns_pivot[df_ns_pivot['ORDER_REF'].isin(mismatch_list_ns)]

    ## Rename the columns and Merge this to missmatch dataframes
    filtered_mismatch_ns.rename(columns={'AMOUNT_FOREIGN': 'GROSS'}, inplace=True)

    # Filter to get transactions where ORDER_REF matches any reference in filtered_mismatch_sett.
    missed_or_missinterpereted = df_sett[df_sett['ORDER_REF'].isin(list(filtered_mismatch_sett['ORDER_REF']))]

    # Append 'Refund' to 'ORDER_REF' where 'TYPE' is marked as 'Refund'.
    missed_or_missinterpereted['ORDER_REF'] = np.where(missed_or_missinterpereted['TYPE'] == 'Refund',
                                                       missed_or_missinterpereted['ORDER_REF'] + 'Refund',
                                                       missed_or_missinterpereted['ORDER_REF'])

    # Group by key columns and calculate the sum for 'NET', 'FEE', and 'GROSS' values.
    missed_or_missinterpereted = missed_or_missinterpereted.groupby(['MERCHANT_ACCOUNT',
                                                                     'BATCH_NUMBER',
                                                                     'ORDER_REF',
                                                                     'CURRENCY']).agg({'NET': 'sum',
                                                                                       'FEE': 'sum',
                                                                                       'GROSS': 'sum'}).reset_index()

    # Create an index column based on 'ORDER_REF' for mapping and merging operations.
    missed_or_missinterpereted['ORDER_REF_index'] = missed_or_missinterpereted['ORDER_REF']
    missed_or_missinterpereted.set_index('ORDER_REF_index', inplace=True)

    # Append 'missed_or_missinterpereted' to 'list_off_missmatch' to collect mismatches.
    missed_or_missinterpereted['Total_in_netsuite'] = missed_or_missinterpereted['ORDER_REF'].map(df_ns_pivot['AMOUNT_FOREIGN']).fillna(0)
    list_off_missmathc.append(missed_or_missinterpereted)

    # If no mismatches are found, print a message. Otherwise, analyze and report mismatches.
    if missed_or_missinterpereted.empty:
        print(f'The {merchant_account} - {batch_number} missing in NetSuite,the list will be provided.')
    else:
        # Loop over each batch number within 'missed_or_missinterpereted' to calculate differences.
        for batch_number, group in missed_or_missinterpereted.groupby('BATCH_NUMBER'):
            merchant_account = merchant_account

            ## To compare all the required accounting columns
            total_netsuite = group['Total_in_netsuite'].sum()
            total_gross = group['GROSS'].sum()
            fee_check = group[group['FEE'] == group['Total_in_netsuite']]
            fee_check_count = fee_check.shape[0]
            difference = total_netsuite - total_gross

            # Verify if Refund is present in ORDER_REF and count occurrences.
            refund = group['ORDER_REF'].str.contains('Refund', na=False)
            refund_count = refund.sum()  # Count of 'True' values

            # Output difference information, specifying if refunds contribute to mismatches.
            if refund_count > 0:
                refund_related = refund.value_counts().get(True, 0)  # Default to 0 if no True values
                print(
                    f'The {merchant_account} has {difference} difference in batch {batch_number}. This issue caused by fee assigned to NetSuite as Gross value with {fee_check_count} entries and there are {refund_related} issues related to refunds.')
            else:
                print(
                    f'The {merchant_account} has {difference} difference in batch {batch_number}. This issue caused by fee assigned to NetSuite as Gross value with {fee_check_count} entries.')


# Run 'checker' function for each merchant account and batch number combination.
for merchant_account in list_of_all_the_merchant_accounts:
    for batch_number in list_of_all_the_batch_number:
        checker(merchant_account,int(batch_number))

# Filter out empty DataFrames from 'missing_in_ns', 'missing_in_sett', and 'list_off_missmathc' lists.
missing_in_netsuite = [df for df in missing_in_ns if not df.empty]
missing_in_settlement = [df for df in missing_in_sett if not df.empty]
missmatch_between_nt_and_st = [df for df in list_off_missmathc if not df.empty]

#%% Missmatch_cases
#EUR138
eur_138_case = missmatch_between_nt_and_st[0]

eur_138_case['amount_check1'] = eur_138_case['NET'] ==eur_138_case['Total_in_netsuite']
eur_138_case['amount_check2'] = eur_138_case['FEE'] ==eur_138_case['Total_in_netsuite']
eur_138_case['amount_check3'] = eur_138_case['GROSS'] ==eur_138_case['Total_in_netsuite']

check_net = eur_138_case.amount_check1.value_counts()
check_fee = eur_138_case.amount_check2.value_counts() ##
check_gross = eur_138_case.amount_check3.value_counts()

# AS IT CAN seen from the Column amount_check2 when the batch 139 was mapped 255
# cases missasigned the FEE instead of GROSS.

settlement_misstotal_eur_138=eur_138_case['GROSS'].sum()
netsuite_missmatch_eur_138 = eur_138_case['Total_in_netsuite'].sum()

eur_138_missing_total  = netsuite_missmatch_eur_138 - settlement_misstotal_eur_138

print(f'The missing netsuite data for {eur_138_case.MERCHANT_ACCOUNT.unique()}  batch number 138 is available in eur_138_case'
      f' dataframe and the total is {eur_138_missing_total} EUR. The problems caused due to fee column asssinged as AMOUNT_FOREIGN for {eur_138_case.shape[0]} transaction which is all of the issues happened in {eur_138_case.MERCHANT_ACCOUNT.unique()}  batch number 138 ')


eur_139_case = missmatch_between_nt_and_st[1]
eur_139_case['amount_check1'] = eur_139_case['GROSS'] ==eur_139_case['Total_in_netsuite']

missmatch_related_gross_eur_139 = eur_139_case.GROSS.sum()
missmatch_related_netsuite_eur_139 = eur_139_case.Total_in_netsuite.sum()

## The refunds are processed in Settlement data but they are missing in netsuite so those 78 case causes 11078 EUR
# difference due to mismatches.

#%% Missing in Netsuite Cases
## 1. EUR

eur_missing_data_in_netsuite = missing_in_netsuite[3]
missing_data_total_in_statament_eur_139= eur_missing_data_in_netsuite.GROSS.sum()

total_isssue_in_eur_139 = missmatch_related_netsuite_eur_139 - missmatch_related_gross_eur_139  - missing_data_total_in_statament_eur_139

# There are 3 ORDER_REF in batch 139 and those are available in settlement but missing in Netsuite and this cause -451 eur
# difference from between settlement and netsuite

print(f'The missing netsuite data for {eur_missing_data_in_netsuite.merchant_account.unique()}  batch number 139 is available in eur_missing_data_in_netsuite, eur_139_case'
      f' dataframe and the total is {total_isssue_in_eur_139} EUR. The problems caused due to refunds and 3 missing transaction which were again refunds.')

#%%
## 2. GBP
gbp_misisng_data_in_netsuite=missing_in_netsuite[0]
missing_gbp_data= list(gbp_misisng_data_in_netsuite['ORDER_REF'])

check_ib_netsuite_gbp = df_all_netsuite_data_wo_constrain_GBP[df_all_netsuite_data_wo_constrain_GBP['ORDER_REF'].isin(missing_gbp_data)]

check_ib_netsuite_gbp['ORDER_REF'].value_counts().sort_values(ascending=False)

check_ib_netsuite_gbp_pivot = pd.pivot_table(
    check_ib_netsuite_gbp,
    values=['AMOUNT', 'AMOUNT_FOREIGN'],
    index=['ORDER_REF','TRANSACTION_TYPE'],
    aggfunc={'AMOUNT': 'sum', 'AMOUNT_FOREIGN': 'sum', 'ORDER_REF': 'count'}
).rename(columns={'ORDER_REF': 'ORDER_REF_COUNT'}).reset_index()

check_ib_netsuite_gbp[['TYPE_NAME','TRANSACTION_TYPE','ACCOUNTNUMBER']].value_counts()

#TYPE_NAME            TRANSACTION_TYPE  ACCOUNTNUMBER
#Accounts Receivable  Invoice           311000           3031
#Deferred Revenue     Invoice           384000           3031
#Accounts Receivable  Credit Note       311000              3
#Deferred Revenue     Credit Note       384000              3
#dtype: int64

# The GB batch 141 is not available in NetSuite. Initially, invoices are generated with Accounts Receivable
# and then moved to Deferred Revenue. Later, three of these invoices were reissued as Credit Notes,
# again involving Accounts Receivable and Deferred Revenue. Consequently, when you run an SQL query
# for only "315720 Receivables against ADYEN-GBP" and "548201 Other Operating Costs," these transactions
# won't appear. Additionally, the batch number is missing in NetSuite, further complicating traceability.

print("The missing netsuite data for ['JetBrainsAmericasEUR'] batch 141 is not available in NetSuite for "
      "the provided accounts. Initially, invoices are generated with Accounts Receivable and "
      "then moved to Deferred Revenue. Later, three of these invoices were reissued as Credit Notes, "
      "again involving Accounts Receivable and Deferred Revenue. Consequently, when running an SQL query for only "
      "'315720 Receivables against ADYEN-GBP' and '548201 Other Operating Costs,' these transactions won't appear. "
      "Additionally, the batch number is missing in NetSuite, further complicating traceability.")

#%%
## 3. AmericasUSD
missed_ausd_141 =missing_in_netsuite[2]

missing_ausd_141= list(missed_ausd_141['ORDER_REF'])

check_ib_netsuite_ausd_141 = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['ORDER_REF'].isin(missing_ausd_141)]
check_ib_netsuite_ausd_141_merch_ac = check_ib_netsuite_ausd_141[check_ib_netsuite_ausd_141['MERCHANT_ACCOUNT']=='JetBrainsAmericasUSD']

check_ib_netsuite_ausd_141_pivot = pd.pivot_table(
    check_ib_netsuite_ausd_141_merch_ac,
    values=['AMOUNT', 'AMOUNT_FOREIGN'],
    index=['ORDER_REF','TRANSACTION_TYPE'],
    aggfunc={'AMOUNT': 'sum', 'AMOUNT_FOREIGN': 'sum', 'ORDER_REF': 'count'}
).rename(columns={'ORDER_REF': 'ORDER_REF_COUNT'}).reset_index()

check_ib_netsuite_ausd_141[['TYPE_NAME','TRANSACTION_TYPE','ACCOUNTNUMBER']].value_counts()

ausd_batch_not_available = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['MERCHANT_ACCOUNT']=='JetBrainsAmericasUSD']
ausd_batch_not_available = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['BATCH_NUMBER'].isna()]

usd_accounts = [315710,548201]
ausd_batch_not_available = ausd_batch_not_available[ausd_batch_not_available['ACCOUNTNUMBER'].isin(usd_accounts)]

netsuite_ausd_141 = ausd_batch_not_available[ausd_batch_not_available['ORDER_REF'].isin(missing_ausd_141)]

print(f'The missing netsuite data for {netsuite_ausd_141.MERCHANT_ACCOUNT.unique()} is available in netsuite_ausd_141'
      f' dataframe and the total is {netsuite_ausd_141.AMOUNT_FOREIGN.sum()} USD so its fully matching. The problem occured '
      f' because the batch number was missing.')

#%%
missed_ausd_139 =missing_in_netsuite[1]

missing_ausd_139= list(missed_ausd_139['ORDER_REF'])

check_ib_netsuite_ausd_139 = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['ORDER_REF'].isin(missing_ausd_139)]
check_ib_netsuite_ausd_139_merch_ac = check_ib_netsuite_ausd_139[check_ib_netsuite_ausd_139['MERCHANT_ACCOUNT']=='JetBrainsAmericasUSD']

check_ib_netsuite_ausd_139_pivot = pd.pivot_table(
    check_ib_netsuite_ausd_139_merch_ac,
    values=['AMOUNT', 'AMOUNT_FOREIGN'],
    index=['ORDER_REF','TRANSACTION_TYPE'],
    aggfunc={'AMOUNT': 'sum', 'AMOUNT_FOREIGN': 'sum', 'ORDER_REF': 'count'}
).rename(columns={'ORDER_REF': 'ORDER_REF_COUNT'}).reset_index()

check_ib_netsuite_ausd_139[['TYPE_NAME','TRANSACTION_TYPE','ACCOUNTNUMBER']].value_counts()

ausd_batch_not_available_139 = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['MERCHANT_ACCOUNT']=='JetBrainsAmericasUSD']
ausd_batch_not_available_139 = df_all_netsuite_data_wo_constrainAUSD[df_all_netsuite_data_wo_constrainAUSD['BATCH_NUMBER'].isna()]

usd_accounts = [315710,548201]
ausd_batch_not_available_139 = ausd_batch_not_available[ausd_batch_not_available['ACCOUNTNUMBER'].isin(usd_accounts)]

netsuite_ausd_139 = ausd_batch_not_available[ausd_batch_not_available['ORDER_REF'].isin(missing_ausd_139)]

# Because the batch number is missing so the matching proces is not done properly.

print(f'The missing netsuite data for {netsuite_ausd_139.MERCHANT_ACCOUNT.unique()} is available in netsuite_ausd_139'
      f' dataframe and the total is {netsuite_ausd_139.AMOUNT_FOREIGN.sum()} USD so its fully matching. The problem occured '
      f' because the batch number was missing.')
