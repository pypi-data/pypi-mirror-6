import csv, random, string


with open('random.csv', 'wb') as f:
    csvwriter = csv.writer(f, delimiter=',', quotechar='"')
    csvwriter.writerow(["Item Type", "Product Name", "Product Type", "Product Code/SKU", "Bin Picking Number", "Brand Name", "Option Set", "Option Set Align", "Product Description", "Price", "Cost Price", "Retail Price", "Sale Price", "Fixed Shipping Cost", "Free Shipping", "Product Warranty", "Product Weight", "Product Width", "Product Height", "Product Depth", "Allow Purchases?", "Product Visible?", "Product Availability", "Track Inventory", "Current Stock Level", "Low Stock Level", "Category", "Product Image ID - 1", "Product Image File - 1", "Product Image Description - 1", "Product Image Is Thumbnail - 1", "Product Image Sort - 1", "Search Keywords"])

    for _ in range(30000):
        random_name = "".join( [random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(10, 36))] )
        random_sku = "".join( [random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(4, 30))] )
        random_desc = "".join( [random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(600, 2000))] )
        csvwriter.writerow(["Product", random_name, "P", random_sku, "", "", "test set", "Right", random_desc, "5", "0", "0", "0", "0", "N", "", "0", "0", "0", "0", "Y", "Y", "", "none", "0", "0", "test", "", "http://www.theretrobaby.com/product_images/q/239/bbear-onzi-101__32153_zoom.jpg"])
        csvwriter.writerow(["Rule", "[S]colors=Black", "", "", "", "", "", "", "", "[ADD]4", "", "", "", "", "", "", "", "", "", "", "Y", "Y"])
        csvwriter.writerow(["Rule", "[S]colors=Blue", "", "", "", "", "", "", "", "[ADD]9", "", "", "", "", "", "", "", "", "", "", "Y", "Y", "", "", "", "", "", "", "", "", "", "", ""])
        csvwriter.writerow(["Rule", "[S]colors=Red", "", "", "", "", "", "", "", "[ADD]4", "", "", "", "", "", "", "", "", "", "", "Y", "Y"])
        csvwriter.writerow(["Rule", "[S]colors=Green", "", "", "", "", "", "", "", "[ADD]9", "", "", "", "", "", "", "", "", "", "", "Y", "Y", "", "", "", "", "", "", "", "", "", "", ""])

# trying: 30000 products (4 options/rules ea), ~51.2MB