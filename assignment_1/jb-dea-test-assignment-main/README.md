# JetBrains Data Engineering & Analysis Test Assignment Instructions



This test assignment is designed to familiarize you with JetBrains Data Engineering & Analysis daily tasks. Also, it is designed to make you aware of our database structure. Both tasks are real business cases that our team has solved. The database structure was reduced, nevertheless, table and column names are identical. Some sensitive facts were changed, and data were randomly generated to protect our internal information.

Feel free to use any software, programming language, database, and approach you prefer. Save your answers with all solution steps (source code and files) to your GitHub storage and send us a link. We provide our detailed feedback by email.

The most important is the correctness and fullness of the answer. In addition, we will evaluate the following aspects:
* the way how the test assignment was solved
* code readability
* used technology

## Task 1: Data quality – the difference between NetSuite ERP and payment gateway
### Business description
JetBrains company provides different payment methods to customers. The most convenient way is an online card payment via the payment gateway Adyen. The great advantage of online payment is speed, the software license key can be activated and used immediately after the payment.

According to accounting principles and rules, we must properly and fully book all transactions. In our case, it means processing several CSV settlement files every month. Settlement processing is fully automated now, but previous CSV files were processed manually by an external tool. Unfortunately, there were several unknown and not logged errors during settlement processing. As a result, there are differences between our accounting software NetSuite, and settlement reports, which must be identified and fixed asap.

The accounting department provided an overall comparison by a batch number and a merchant account. 

|Merchant Account|Batch Number|NetSuite|Payment Gateway|Difference|
| ------------- | ------ | ------ | ------ | ------ |
|JetBrainsAmericasUSD||22,298,648|0|22,298,648|
|JetBrainsAmericasUSD|138|9,445,798|9,445,798|0|
|JetBrainsAmericasUSD|139|0|11,255,775|-11,255,775|
|JetBrainsAmericasUSD|140|11,256,666|11,256,666|0|
|JetBrainsAmericasUSD|141|0|11,042,873|-11,042,873|
|JetBrainsAmericasUSD|142|7,581,479|7,581,479|0|
|JetBrainsEUR|138|11,235,135|11,318,386|-83,251|
|JetBrainsEUR|139|13,463,478|13,451,949|11,529|
|JetBrainsEUR|140|13,268,388|13,268,388|0|
|JetBrainsEUR|141|13,165,714|13,165,714|0|
|JetBrainsEUR|142|9,127,436|9,127,436|0|
|JetBrainsGBP|138|870,196|870,196|0|
|JetBrainsGBP|139|1,065,368|1,065,368|0|
|JetBrainsGBP|140|1,089,633|1,089,633|0|
|JetBrainsGBP|141|0|1,021,258|-1,021,258|
|JetBrainsGBP|142|735,494|735,494|0|
|JetBrainsUSD|138|1,762,238|1,762,238|0|
|JetBrainsUSD|139|2,156,538|2,156,538|0|
|JetBrainsUSD|140|2,088,749|2,088,749|0|
|JetBrainsUSD|141|2,026,363|2,026,363|0|
|JetBrainsUSD|142|1,410,287|1,410,287|0|

Column *NetSuite* – a sum of all Payments and Customer Deposits foreign amounts on accounts:
* 315700 JBCZ: Receivables against ADYEN-EUR
* 315710 JBCZ: Receivables against ADYEN-USD
* 315720 JBCZ: Receivables against ADYEN-GBP
* 315800 JBA: Receivable from Adyen - USD
* 548201 Other operating costs

Column *Payment gateway* – a sum of Adyen settlement overview, equal to the content of CSV settlement files.
### Task
Analyze and provide a list of all differences on transaction level between NetSuite and payment gateway. Do not forget to compare all accounting-relevant columns.

### Technical information
CSV settlement files are stored in the settlement folder.

All relevant data is stored on SQL Server, database `dea`, schema `netsuite`.

## Task 2: Sale analysis – revenue decline in ROW region
### Business description
JetBrains company sells software products all over the world. We have two big sales teams:

1) US – sales representatives responsible for the huge American market with top IT companies.
2) ROW – the rest of the world, Wien-based team responsible for sales worldwide except for the US.

Both formally independent teams cooperate very closely and intensively. The vast majority of US and ROW sales campaigns are planned and launched together. However, every market has different local factors that need to be considered, so there are also small local sales campaigns.

Revenue YTD growth is the most important metric for both sales teams. The metric is downloaded from the Summary report on a daily basis, written with chalk on a blackboard, and discussed in weekly meetings. Both teams achieved similar results 2017 vs 2018. Unfortunately, ROW 2019H1 sales team performance is getting significantly worse than American. American and ROW sales regional managers have discussed their 2019 strategies several times, but they haven’t found any reason of ROW decline.

### Task
ROW regional manager asks you to analyze the difference, find out the source of the issue and recommend action steps.
### Technical information
All relevant data is stored on SQL Server, database `dea`, schema `sales`. Source code of summary report:
```
SELECT cou.region,
  SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) as SalesUsd2018H1,
  SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) as SalesUsd2019H1
FROM dea.sales.Orders ord
JOIN dea.sales.OrderItems ordItm ON ord.id = ordItm.order_id
JOIN dea.sales.Customer cust ON ord.customer = cust.id
JOIN dea.sales.Country cou ON cust.country_id = cou.id
JOIN dea.sales.ExchangeRate exRate ON ord.exec_date = exRate.date AND ord.currency = exRate.currency
JOIN dea.sales.Product prod ON ordItm.product_id = prod.product_id
WHERE ord.is_paid = 1 -- Only paid orders, exclude pre-orders
  AND YEAR(ord.exec_date) IN (2018, 2019) -- Year 2018, 2019
  AND MONTH(ord.exec_date) BETWEEN 1 AND 6 -- H1
GROUP BY cou.region
ORDER BY 1
;
```
