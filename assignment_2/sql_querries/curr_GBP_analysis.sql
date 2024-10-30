With usd_case as (SELECT
                      cou.region AS region,
                      ordItm.product_id AS product_id,
                      ordItm.license_type AS license_type,
                      YEAR(ord.exec_date) AS year,
                      MONTH(ord.exec_date) AS month,
                      ord.customer AS customer,
                      ord.currency AS currency,
                      ord.is_reseller AS reseller_flag,
                      cust.name AS customer_name,
                      cust.type_id AS customer_type_id,
                      cust.country_id AS country_id,
                      cou.name AS country_name,
                      cou.iso AS country_iso,
                      cou.region AS country_region,  -- Consider removing one of the 'region' references
                      cou.currency AS currency_flag_cou,
                      prod.product_family AS product_family,
                      prod.name AS product_name,
                      AVG(prod.price) as product_price,
                      CASE
                          WHEN MONTH(ord.exec_date) BETWEEN 1 AND 6 THEN 'H1'
                          ELSE 'H2'
                          END AS half_year_flag,
                      SUM(ordItm.amount_total) AS local_amount,
                      SUM(ordItm.quantity) AS total_qty,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.quantity
                              ELSE 0.00
                          END) AS SalesQuantity2018H1,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.quantity
                              ELSE 0.00
                          END) AS SalesQuantity2019H1,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total / exRate.rate
                              ELSE 0.00
                          END) AS SalesUsd2018H1,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total / exRate.rate
                              ELSE 0.00
                          END) AS SalesUsd2019H1,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2019 THEN ordItm.amount_total
                              ELSE 0.00
                          END) AS SalesOwn_Curr2019H1,
                      SUM(CASE
                              WHEN YEAR(ord.exec_date) = 2018 THEN ordItm.amount_total
                              ELSE 0.00
                          END) AS SalesOwn_Curr2018H1

                  FROM dea.sales.Orders ord
                           JOIN dea.sales.OrderItems ordItm ON ord.id = ordItm.order_id
                           JOIN dea.sales.Customer cust ON ord.customer = cust.id
                           JOIN dea.sales.Country cou ON cust.country_id = cou.id
                           JOIN dea.sales.ExchangeRate exRate ON ord.exec_date = exRate.date AND ord.currency = exRate.currency
                           JOIN dea.sales.Product prod ON ordItm.product_id = prod.product_id
                  WHERE ord.is_paid = 1  -- Only paid orders, exclude pre-orders
                    AND YEAR(ord.exec_date) IN (2018, 2019)
                    --and cou.name = 'Korea'
                    and MONTH(ord.exec_date) BETWEEN 1 AND 6
                  GROUP BY
                      cou.region, ordItm.product_id, ordItm.license_type,
                      YEAR(ord.exec_date), MONTH(ord.exec_date),
                      ord.customer, ord.currency, ord.is_reseller,
                      cust.name, cust.type_id, cust.country_id,
                      cou.name, cou.iso, cou.region, cou.currency,
                      prod.product_family, prod.name,
                      CASE
                          WHEN MONTH(ord.exec_date) BETWEEN 1 AND 6 THEN 'H1'
                          ELSE 'H2'
                          END
)

SELECT  usd_case.country_name,
        product_family,
        Sum(usd_case.SalesQuantity2018H1) as sales_in_2018,
        Sum(usd_case.SalesQuantity2019H1) as sales_in_2019,
        (Sum(usd_case.SalesQuantity2019H1) / SUM(usd_case.SalesQuantity2018H1) -1)*100 as Yoy_Quantity_Perc,
        AVG(product_price) as unit_price ,
        Sum(usd_case.SalesOwn_Curr2018H1) as sales_own_curr_2018,
        Sum(usd_case.SalesUsd2018H1) as sales_usd_2018,
        Sum(usd_case.SalesOwn_Curr2019H1) as sales_own_curr_2019,
        Sum(usd_case.SalesUsd2019H1) as sales_usd_2019,
        (Sum(usd_case.SalesOwn_Curr2019H1) / SUM(usd_case.SalesOwn_Curr2018H1) -1)*100 as Yoy_Own_Curr_Perc,
        (Sum(usd_case.SalesUsd2019H1) / SUM(usd_case.SalesUsd2018H1) -1)*100 as Yoy_USD_Perc,
        (Sum(usd_case.SalesUsd2019H1)-Sum(usd_case.SalesUsd2018H1)) as Difference_in_USD,
        SUM((SUM(usd_case.SalesUsd2019H1) - SUM(usd_case.SalesUsd2018H1)))
            OVER (PARTITION BY usd_case.country_name) AS country_total,
        SUM((SUM(usd_case.SalesUsd2019H1) - SUM(usd_case.SalesUsd2018H1))) OVER () total
FROM usd_case
Where region = 'ROW'
  And currency = 'GBP'
GROUP BY country_name, product_family
Order By country_name,product_family
