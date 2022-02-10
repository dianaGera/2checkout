data = {
    "AdditionalInfo": None,

    "CustomPriceBillingCyclesLeft": 1,
    "DeliveryInfo": {
        "Codes": [
            {
                "Code": "___TEST___CODE____",
                "Description": None,
                "ExtraInfo": None,
                "File": None
            }
        ],
        "Description": None
    },
    "EndUser": {
        "CustomerReference": None,
        "Address1": "Test Address",
        "Address2": "",
        "City": "",
        "Company": "",
        "CountryCode": "us",
        "Email": "customer@2Checkout.com",
        "Fax": "",
        "FirstName": "Customer",
        "Language": "",
        "LastName": "2Checkout",
        "Phone": "",
        "State": "CA",
        "Zip": "12345"
    },
    "ExpirationDate": "",
    "ExternalCustomerReference": None,
    "ExternalSubscriptionReference": None,
    "NextRenewalPrice": 0,
    "NextRenewalPriceCurrency": "usd",
    "PartnerCode": "",
    "Payment": {
        "CCID": "",
        "CardNumber": "",
        "CardType": "",
        "ExpirationMonth": "",
        "ExpirationYear": "",
        "HolderName": ""
    },
    "Product": {
        "PriceOptionCodes": [
            ""
        ],
        "ProductCode": "",
        "ProductId": "",
        "ProductName": "",
        "ProductQuantity": 1,
        "ProductVersion": ""
    },
    "StartDate": "",
    "SubscriptionValue": 0,
    "SubscriptionValueCurrency": "usd",
    "Test": 1
}


promotion = {
    "Type": "REGULAR",
    "ApplyRecurring": None,
    "ChannelType": "ECOMMERCE",

    "Coupon": {
        "Codes": [
            "code1",
            "code2"
        ],
        "Type": "MULTIPLE"
    },
    "Description": "Promo description1",
    "Discount": {
        "Type": "PERCENT",
        "Value": 41
    },
    "Enabled": True,
    "EndDate": None,
    "InstantDiscount": 0,
    "MaximumOrdersNumber": None,
    "MaximumQuantity": None,
    "Name": "Promo percentage REST",
    "Products": [
        {
            "Code": "my_subscription_1"
        }
    ],
    "PublishToAffiliatesNetwork": 0,
    "StartDate": None
}