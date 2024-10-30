SELECT
    cou.region,
    cou.currency,

    SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total ELSE 0.00 END) AS SalesOwnCurr2018H1,
    SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total ELSE 0.00 END) AS SalesOwnCurr2019H1,

    -- Calculate the difference in own currency
    SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total ELSE 0.00 END) -
    SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total ELSE 0.00 END) AS DifferenceOwnCurr,
    ROUND(
            (SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total ELSE 0.00 END) -
             SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total ELSE 0.00 END))
                / NULLIF(SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total ELSE 0.00 END), 0) * 100,
            2
    ) AS DifferencePercentageOwnCurr,
    -- Calculate USD sales and their difference
    SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) AS SalesUsd2018H1,
    SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) AS SalesUsd2019H1,

    SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) -
    SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) AS DifferenceInUSDPerCurrency,
    ROUND(
            (SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) -
             SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END))
                / NULLIF(SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate  ELSE 0.00 END), 0) * 100,
            2
    ) AS DifferencePercentageUSD,
    -- Total of DifferenceInUSD per region and currency
    SUM(SUM(CASE WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END) -
        SUM(CASE WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate ELSE 0.00 END))
        OVER (PARTITION BY cou.region) AS TotalInUSD

FROM dea.sales.Orders ord
         JOIN dea.sales.OrderItems ordItm ON ord.id = ordItm.order_id
         JOIN dea.sales.Customer cust ON ord.customer = cust.id
         JOIN dea.sales.Country cou ON cust.country_id = cou.id
         JOIN dea.sales.ExchangeRate exRate ON ord.exec_date = exRate.date AND ord.currency = exRate.currency
         JOIN dea.sales.Product prod ON ordItm.product_id = prod.product_id

WHERE ord.is_paid = 1 -- Only paid orders, exclude pre-orders
  AND YEAR(ord.exec_date) IN (2018, 2019) -- Years 2018 and 2019
  AND MONTH(ord.exec_date) BETWEEN 1 AND 6 -- H1 only

GROUP BY cou.region, cou.currency
ORDER BY cou.region, cou.currency;
