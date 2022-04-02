import sys
import re
import pandas as pd
import time
import datetime
import random


class Transactions:
    species = "Canis familiaris"

    def __init__(self, rewardsMember=False):
        self.rewardsMember = rewardsMember
        self.cart = []
        self.CartDF = pd.DataFrame(columns=["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"])
        self.InventoryDF = pd.read_csv('inventory.txt', header=None, sep='[:,]',
                                       engine="python",
                                       names=["Item", "Quantity",
                                              "Regular Price",
                                              "Member Price",
                                              "Tax Status"], )
        self.Subtotal = 0
        self.TAX = 0
        self.Total = 0
        self.TotalSold = 0
        print(self.InventoryDF)

    # Add items to cart
    def add_items(self):
        itemID = int(input("Enter ID (0-10) item to add: "))
        if itemID in self.InventoryDF.index:
            number = int(input("Number of items to add: "))
            if number <= (self.InventoryDF.iloc[itemID]["Quantity"]):

                if self.rewardsMember == True:
                    prices = self.InventoryDF["Member Price"].replace('[\$,]', '', regex=True).astype(float)
                else:
                    prices = self.InventoryDF["Regular Price"].replace('[\$,]', '', regex=True).astype(float)

                unit_price = prices[itemID]

                newDF = pd.DataFrame([[self.InventoryDF.iloc[itemID]["Item"], number, unit_price, unit_price * number,
                                       self.InventoryDF.iloc[itemID]["Tax Status"]]],
                                     columns=["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"])
                CartDF = pd.concat([self.CartDF, newDF])
                self.CartDF = CartDF.groupby(["ITEM", "UNIT PRICE", "TAX STATUS"], as_index=False)[
                    ["QUANTITY", "TOTAL"]].sum()

                # if not self.CartDF.empty:
                #    print(self.CartDF)
                print("Item added")

            else:
                print("There are not enought items on inventory")
        else:
            print("Item doesn't exist on inventory")

    # Remove individual items
    def remove_item(self):
        itemID = int(input("Enter ID cart item to remove: "))
        if itemID in self.CartDF.index:
            self.CartDF.drop(itemID, inplace=True)
            print("Item removed")
            # if not self.CartDF.empty:
            #    print(self.CartDF)
        else:
            print("Item doesn't exist on cart")

    # Remove all items
    def empty_cart(self):
        self.CartDF = pd.DataFrame(columns=["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"])

    def update_cost(self):
        if not self.CartDF.empty:
            self.Subtotal = self.CartDF['TOTAL'].sum()

            self.CartDF["TAX"] = [total * 6.5 / 100
                                  if ts == " Taxable"
                                  else 0
                                  for ts, total in zip(self.CartDF["TAX STATUS"], self.CartDF["TOTAL"])]
            self.TAX = self.CartDF['TAX'].sum()

            self.Total = self.Subtotal + self.TAX

            self.TotalSold = self.CartDF['QUANTITY'].sum()

    def view_cart(self):
        if self.CartDF.empty:
            print('Cart is empty!')
        else:
            self.update_cost()
            self.CartDF = self.CartDF[["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"]]
            CartDF = self.CartDF[["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL"]]
            print(CartDF)
            print("**********")
            print("Sub-total: $", self.Subtotal)
            print("TAX (6.5%): $", self.TAX)
            print("Total: $", self.Total)

    def checkout(self):
        if self.CartDF.empty:
            print('Cart is empty!')
        else:
            self.update_cost()
            self.CartDF = self.CartDF[["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"]]

            while True:
                cash = int(input("Put cash received (>= total cost " + str(self.Total) + "): $"))
                print("\n")
                if not cash < self.Total:
                    break

            CartDF = self.CartDF[["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL"]]
            print("**********")
            today = datetime.date.today()
            dateT = today.strftime("%B %d, %Y")
            dateP = today.strftime("%m%d%y")
            print(dateT)
            tnumber = random.randint(000000, 999999)
            print("TRANSACTION: ", tnumber)
            print("**********")
            print(CartDF)
            print("**********")
            print("Total number of items sold: $", self.TotalSold)
            print("Sub-total: $", round(self.Subtotal, 2))
            print("TAX (6.5%): $", round(self.TAX, 2))
            print("Total: $", round(self.Total, 2))
            print("Cash: $", round(cash, 2))
            print("Change: $", round(cash - self.Total, 2))

            # save receip in txt file
            print("\nSaving receipt ....")
            filename = 'transaction_' + str(tnumber) + '_' + str(dateP) + '.txt'
            CartDF.to_csv(filename)
            with open(filename, 'a') as fd:
                fd.write("\n************************\n")
                fd.write(dateT)
                fd.write("\nTotal number of items sold: $" + str(self.TotalSold))
                fd.write("\nSub-total: $" + str(round(self.Subtotal, 2)))
                fd.write("\nTAX (6.5%): $" + str(round(self.TAX, 2)))
                fd.write("\nTotal: $" + str(round(self.Total, 2)))
                fd.write("\nCash: $" + str(round(cash, 2)))
                fd.write("\nChange: $" + str(round(cash - self.Total, 2)))
            print("\nSaved receipt ....")

            # inventory updated
            print("\nUpdating inventory ....\n")
            if not self.CartDF.empty:

                for index,items,quantity in zip(self.InventoryDF.index,self.InventoryDF["Item"], self.InventoryDF["Quantity"]):
                    df=self.CartDF.loc[self.InventoryDF["Item"] == items]
                    if not df.empty:
                        itemName = df["ITEM"].values[0]
                        itemQuantity = df["QUANTITY"].values[0]
                        rest= self.InventoryDF.iloc[index]["Quantity"]  - itemQuantity
                        self.InventoryDF.at[index,"Quantity"] = rest
                        print(self.InventoryDF)

            print("\nInventory updated....\n")

            # empty cart
            self.CartDF = self.CartDF = pd.DataFrame(columns=["ITEM", "QUANTITY", "UNIT PRICE", "TOTAL", "TAX STATUS"])

    def cancel_transaction(self):
        sys.exit()


def main():
    user = Transactions()
    option = input("Are you a rewards member Y/N: ")
    if option.lower() == "y":
        user.rewardsMember = True

    while True:
        print(
            """\n
            --------------------------------------
                    Transaction Options
            --------------------------------------
            1. Add items
            2. Remove items
            3. Empty cart
            4. View cart
            5. Checkout
            6. Cancel transaction
            --------------------------------------
            """
        )

        option = int(input("Enter an option: "))

        if option == 6:
            user.cancel_transaction()
        if option == 1:
            # df = view_inventory()
            print("\n--------------------------------------")
            # itemID = int(input("Enter ID (0-10) item to add: "))
            # number = int(input("Number of items to add: "))
            user.add_items()
            # print("Item added: ", df.iloc[itemID]["Item"])
            print("--------------------------------------")
            time.sleep(2)

        if option == 2:
            print("\n--------------------------------------")
            user.remove_item()
            print("--------------------------------------")
            time.sleep(5)

        if option == 3:
            print("\n--------------------------------------")
            print("    Cart Empty ")
            print("--------------------------------------")
            user.empty_cart()
            time.sleep(5)

        if option == 4:
            print("\n--------------------------------------")
            print("    View cart ")
            print("--------------------------------------")
            user.view_cart()
            time.sleep(5)

        if option == 5:
            print("\n--------------------------------------")
            print("    Checkout")
            print("--------------------------------------")
            user.checkout()
            time.sleep(5)


if __name__ == '__main__':
    main()
