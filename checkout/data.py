payment_data = {
        "Country": "br",
        "Currency": "usd",
        "CustomerIP": "91.220.121.21",
        "ExternalReference": "REST_API_AVANGTE",
        "Language": "en",
        "BillingDetails": {
            "Address1": "Test Address",
            "City": "LA",
            "CountryCode": "BR",
            "Email": "dianamatkava@gmail.com",
            "FirstName": "Customer",
            "LastName": "2Checkout",
            "Phone": "null",
            "State": "null",
            "Zip": "null",
            "FiscalCode": "null",
        },
        "Items": [
            {
                "Code": "39IBDTJYCE",
                "Quantity": "1",
                "Promotion": 'IGH4XAULT3',
                "Trial": 'true'
            }
        ],
        "PaymentDetails": {
            "Type": "CC",
            "Currency": "usd",
            "CustomerIP": "91.220.121.21",
            "PaymentMethod": {
                "CCID": "123",
                "CardNumber": "378282246310005",
                "CardNumberTime": "12",
                "CardType": "AMEX",
                "ExpirationMonth": "12",
                "ExpirationYear": "2023",
                "HolderName": "John Doe",
                "HolderNameTime": "12",
                "RecurringEnabled": 'true',
                "Vendor3DSReturnURL": "www.test.com",
                "Vendor3DSCancelURL": "www.test.com"
                },
        }
    }

checkout_js = {
  "Country": "br",
  "Currency": "brl",
  "CustomerIP": "91.220.121.21",
  "CustomerReference": "GFDFE",
  "ExternalCustomerReference": "IOUER",
  "ExternalReference": "REST_API_AVANGTE",
  "Language": "en",
  "Source": "testAPI.com",
  "Affiliate": {},
  "BillingDetails": {
    "Address1": "Test Address",
    "City": "LA",
    "CountryCode": "BR",
    "Email": "customer@2Checkout.com",
    "FirstName": "Customer",
    "FiscalCode": "056.027.963-98",
    "LastName": "2Checkout",
    "Phone": "556133127400",
    "State": "DF",
    "Zip": "70403-900"
  },
  "Items": [
    {
      "Code": "39IBDTJYCE",
      "Quantity": "1"
    }
  ],
  "PaymentDetails": {
    "Currency": "BRL",
    "CustomerIP": "91.220.121.21",
    "PaymentMethod": {
      "EesToken": None,
      "RecurringEnabled": 'true',
      "Vendor3DSReturnURL": "www.test.com",
      "Vendor3DSCancelURL": "www.test.com"
    },
    "Type": "TEST"
  }
}

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