## JetBrains Test Assignment

### Task 1: Data quality – the difference between NetSuite ERP and payment gateway

The settlements provided are for the Merchant Account, including JetBrainsAmericasUSD, JetBrainsEUR, JetBrainsGBP, and JetBrainsUSD. For these Merchant Accounts, there are five batches available: 138, 139, 140, 141, and 142. 

The table below displays batches with misalignments between NetSuite and settlement, detailing the reasons and impacts of each mismatch.

| Merchant_Account     | Batch_Number | Number_of_missinterpreted_transactions                                                                                                  | Impact |
|----------------------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------|-|
| JetBrainsAmericasUSD | 139          | 33639 transactions have missing batch number while mapping to netsuite                                                                  | -11,255,775|
| JetBrainsAmericasUSD | 141          | 33037 transactions have missing batch number while mapping to netsuite                                                                  |-11,042,873 |
| JetBrainsEUR         | 138          | 255 missinterpreted (Fee assinged as Gross)                                                                                             | -83,251 |
| JetBrainsEUR         | 139          | 78 (return is not processed) - 3 missing transactions                                                                                   | 11,529 |
| JetBrainsGBP         | 141          | 3031 transactions only mapped Account Receivable not the Deffered Receivables so there is missalingment between netsuite and settlement | 11,529 |

#### JetBrainsAmericasUSD

Batches 138 and 139 are missing in NetSuite. However, there are transactions in NetSuite that lack a batch number.

When transactions with missing batch numbers are compared to the settlement data using the ORDER_REF, they fully match. This discrepancy may have occurred during manual data entry, where transactions were mapped using batch numbers. Because this information was missing in the NetSuite data, the transactions were not mapped correctly.

#### JetBrainsEUR

The total in batches 138 and 139 is not matching with the settlement data.

##### Batch138

There are 255 mismatches between NetSuite and the settlement data, with discrepancies in the transaction amounts. The issue arose because the fee column in the settlement data was mistakenly assigned as the AMOUNT_FOREIGN column in NetSuite for these 255 transactions, resulting in a difference of -83,251 EUR between the settlement and NetSuite data.

##### Batch139

There are 3 transactions present in the settlement data but missing in NetSuite, resulting in a difference of 4,345 EUR.
There are 78 mismatches between NetSuite and the settlement data due to refunds recorded in the settlement data but not reflected in NetSuite, causing a discrepancy of 7,184 EUR.

#### JetBrainsGBP

There is only an issue in batch 141 and its caused 

The missing netsuite data for  batch 141 is not available in NetSuite for the provided accounts. Initially, invoices are generated with Accounts Receivable and 
then moved to Deferred Revenue. Later, three of these invoices were reissued as Credit Notes, again involving Accounts Receivable and Deferred Revenue. Consequently, when running an SQL query for only 
315720 Receivables against ADYEN-GBP' and '548201 Other Operating Costs,' these transactions won't appear.

| #TYPE_NAME          | TRANSACTION_TYPE  |ACCOUNTNUMBER | Transaciton |
|---------------------|-------------------|--------------|-------------|
| Accounts Receivable |  Invoice          | 311000       | 3031        |
| Deferred Revenue    |  Invoice          | 384000       | 3031        |
|Accounts Receivable  |  Credit Note      |  311000      | 3           |
|Deferred Revenue     |  Credit Note      |  384000      | 3           |

#### JetBrainsUSD 

All the USD NetSuite and Settlement files are mathing with each other. 

### Task 2: Sale analysis – revenue decline in ROW region

When the sales in 2018 and 2019 compared with each other by regions ROW has -4,645,339
USD while US has -142,896 USD change in first six months. When started deeply looking in
ROW region there are 8 countries in total which are using USD 4 of them, EUR 3 of them
and GBP. To investigation shows:


**•** The USD-based countries revealed a decrease of 96,738 USD in revenue, attributed to a similar quantity sold but a higher proportion of cheaper items compared to more  expensive ones.

**•** In countries using EUR, despite an increase in the number of items sold and revenue generated in EUR, the converted amount in USD decreased to -4,188,058 USD due to a  7.1% drop in the average exchange rate.

**•** In the GBP-using country, there is a significant gap between revenue generated in  GBP and USD. Although two product families saw increased sales compared to 2018, resulting in profits in GBP, the converted revenue in USD dropped by $360,543 due
to a 6.4% decline in the exchange rate.

**•** The company is not following a local pricing strategy, resulting in year-over-year  changes in product prices of approximately 6.5% due to fluctuations in the exchange rate.

**•** If the foreign exchange (FX) rate remains flat or uses the same exchange rate as in  2018 when calculating sales in the ROW region for 2019, the company will report 76,922,567 USD instead of 72,216,951 USD, reflecting a 0.1% increase rather than a -6.0%  decrease compared to 2018 sales in that region.

Based on these findings, the following insights should be acted upon:

**• Hedging Strategy:** The company should implement or adjust currency hedging strategies to better protect against future exchange rate fluctuations. This approach would enable them to maintain steady reported earnings, thereby reducing the volatility that foreign currency exposure currently adds to their international revenue.

**• Local Pricing Strategy:** The company should consider localized pricing adjustments in foreign markets. The prices remained constant in USD-based countries but fluctuated in EUR and GBP markets, causing skewness in USD reports. By aligning pricing strategies with exchange rate variances, the company can protect its profitability without relying solely on favorable currency conditions