SELECT ORDER_REF,
    AMOUNT,
    AMOUNT_FOREIGN,
    TRANSACTION_TYPE,
    ACCOUNTNUMBER,
    MERCHANT_ACCOUNT,
    BATCH_NUMBER,
       TYPE_NAME

FROM dea.netsuite.TRANSACTIONS  trans
         JOIN dea.netsuite.TRANSACTION_LINES tran_line ON tran_line.TRANSACTION_ID = trans.TRANSACTION_ID
         JOIN dea.netsuite.SUBSIDIARIES subs ON subs.SUBSIDIARY_ID = tran_line.SUBSIDIARY_ID
         JOIN dea.netsuite.CURRENCIES curr ON curr.CURRENCY_ID = trans.CURRENCY_ID
         JOIN dea.netsuite.ACCOUNTS acc ON acc.ACCOUNT_ID = tran_line.ACCOUNT_ID

WHERE MERCHANT_ACCOUNT IN('JetBrainsAmericasUSD')

;
