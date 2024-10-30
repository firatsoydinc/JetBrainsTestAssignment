SELECT cou.region,
       cou.currency as currency,
       COUNT(Distinct (cou.name)) as number_of_countries
FROM dea.sales.Orders ord
         JOIN dea.sales.OrderItems ordItm ON ord.id = ordItm.order_id
         JOIN dea.sales.Customer cust ON ord.customer = cust.id
         JOIN dea.sales.Country cou ON cust.country_id = cou.id
         JOIN dea.sales.ExchangeRate exRate ON ord.exec_date = exRate.date AND ord.currency = exRate.currency
         JOIN dea.sales.Product prod ON ordItm.product_id = prod.product_id
GROUP BY cou.region,cou.currency
ORDER BY 1
;