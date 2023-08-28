from decimal import Decimal

import numpy as np
import pandas as pd


def calc_share_trade_profits(df: pd.DataFrame):
    """
    Calculates the profits of all shares trades using FIFO method in the given data frame.
    The data frame must have the following columns:
    count: Number of traded shares, positive numbers meaning a purchase and negative number meaning a sale.
    debit: Total purchase price (negative number)
    credit: Total selling price (positive number)

    The result is a series with realized profits for all sales.

    All numbers will be converted to decimals internally before doing the calculation.

    Example:
    Two rows, first representing the purchase (e.g. count=100, debit=-1000 for buying 100 shares at 1,000 money) and
    second the sale (e.g. count=-100, credit=1200 for selling 100 shares at 1,200 money), result in a profit of 200
    (1,200 - 1,100 = 200).

    Partial purchases and sales are supported, too, for example buying 100, then 200 shares, and then selling 50,
    then 200, then 50 shares. Profit is calculated using FIFO method.

    :param df: Pandas DataFrame with data from a statements of funds
    :return: Pandas Series with profits
    """
    # Create a temporary data frame with relevant columns only and add the following:
    # remaining: Remaining number of shares of this purchase; positive number, gets smaller with each processed sale until 0
    # profit: Calculated profit of each sale
    # In addition, all values will be converted to decimals as floats are unable to represents financial numbers
    # correctly.
    temp = df.filter(["count", "debit", "credit"])
    temp["credit"] = temp["credit"].fillna(Decimal("NaN")).apply(Decimal)
    temp["debit"] = temp["debit"].fillna(Decimal("NaN")).apply(Decimal)
    temp["remaining"] = temp["count"]
    temp["profit"] = temp["credit"].fillna(Decimal(0))
    stock = 0

    # Calculate profit for each closing (Glattstellung)
    # A profit is generated on each sale as money will flow to the customer at this time and is taxable.
    # For short sales, the first transaction has a profit which might get decreased by later transactions.
    # For long sales, the last transaction has a profit, depending on the previous purchase transactions.
    # Things will get complicated if the trade has several transactions. Profits will be calculated with FIFO.
    for idx in temp.index:
        record = temp.loc[idx]
        stock_decreased = abs(stock + record["count"]) < abs(stock)
        stock += record["count"]
        if not stock_decreased:
            # Stock increased, no need to even with previous transactions
            continue

        # Transaction found which evens previous transactions
        count_to_close = record["count"]
        for prev_idx in temp.index[:idx]:
            prev_record = temp.loc[prev_idx]
            if prev_record["remaining"] == 0:
                # No items for even left, continue with next transaction
                continue

            # Reduce previous transaction as much as possible
            take = min(abs(prev_record["remaining"]), abs(count_to_close)) * np.sign(count_to_close)
            temp.at[prev_idx, "remaining"] += take
            temp.at[idx, "remaining"] -= take
            count_to_close -= take

            # Calculate profit of opening or closing transaction (only transaction with a credit have a profit)
            if pd.isnull(temp.at[idx, "credit"]):
                price = np.nansum([record["debit"], record["credit"]]) / record["count"] * take
                temp.at[prev_idx, "profit"] += price
            else:
                prev_price = np.nansum([prev_record["debit"], prev_record["credit"]]) / prev_record["count"] * take
                temp.at[idx, "profit"] -= prev_price

            if count_to_close == 0:
                break

    return temp["profit"]


def __calc_share_trade_profits(df: pd.DataFrame):
    """
    Calculates the profits of all shares trades using FIFO method in the given data frame.
    The data frame must have the following columns:
    count: Number of traded shares, positive numbers meaning a purchase and negative number meaning a sale.
    debit: Total purchase price (absolute number will be taken)
    credit: Total selling price (absolute number will be taken)

    The result is a series with realized profits for all sales.

    Example:
    Two rows, first representing the purchase (e.g. count=100, debit=-1000 for buying 100 shares at 1,000 money) and
    second the sale (e.g. count=-100, credit=1200 for selling 100 shares at 1,200 money), result in a profit of 200
    (1,200 - 1,100 = 200).

    Partial purchases and sales are supported, too, for example buying 100, then 200 shares, and then selling 50,
    then 200, then 50 shares. Profit is calculated using FIFO method.

    :param df: Pandas DataFrame with data from a statements of funds
    :return: Pandas Series with profits
    """
    # Create a temporary data frame with relevant columns only and add the following:
    # remaining: Remaining number of shares of this purchase; positive number, gets smaller with each processed sale until 0
    # profit: Calculated profit of each sale
    temp = df.filter(["count", "debit", "credit"])
    temp["remaining"] = temp["count"]
    temp["profit"] = 0

    # Calculate the profit for each sale
    for sale_idx in temp.index:
        sales_record = temp.loc[sale_idx]
        if sales_record["count"] >= 0:
            # Skip non-sales records
            continue

        # Shares have been sold => calculate profit and adjust remaining stock
        shares_left = abs(sales_record["count"])

        # Reduce each previous purchase, starting with the first one (FIFO), by shares_left
        # If a previous purchase is not big enough, repeat with next one, and so on
        for purchase_idx in temp.index:
            purchase_record = temp.loc[purchase_idx]
            if purchase_record["remaining"] <= 0:
                # Skip records which have been processed already
                continue

            # Reduce purchase record as much as possible
            take_from_purchase = min(shares_left, purchase_record["remaining"])
            temp.at[purchase_idx, "remaining"] -= take_from_purchase
            shares_left -= take_from_purchase

            # Calculate profit of previous purchase and current sale
            purchase_total = abs(purchase_record["debit"] / purchase_record["count"]) * take_from_purchase
            sales_total = abs(sales_record["credit"] / sales_record["count"]) * take_from_purchase
            temp.at[sale_idx, "profit"] += sales_total - purchase_total

            if shares_left == 0:
                break

    return temp["profit"]
