
import sys
import re
import json
import csv

def load_tracked_products(path):
    with open(path, 'r') as data_file:
        data = json.load(data_file)
        return data

def load_historical_data(path):
    with open(path, 'r') as data_file:
        return [{k: int(v) for k, v in row.items()} for row in csv.DictReader(data_file, skipinitialspace=True)]

def main (argv):

    tracked_products = [TrackedProduct.json_decoder(item) for item in load_tracked_products('products.json')]
    historical_data = load_historical_data('prices.csv')

    for price_row in historical_data:
        historical_data[price_row.id].price_variations.append(PriceVariation(price_row.date, -1, price_row.price))

############################################################

class TrackedProduct(object):

    percentageMatcher = re.compile("([+-]?\d+)%")

    def __init__(self, id, name, url, selector, monitor_interval):
        self.id = id
        self.name = name
        self.url = url
        self.price_selector = selector
        self.triggers = []
        self.emails_to_notify = []
        self.monitor_interval = monitor_interval
        self.price_variations = []

    def add_trigger(self, trigger_text):
        trigger = self.parse_trigger(trigger_text)
        self.triggers.append(trigger)

    def add_email(self, email):
        self.emails_to_notify.append(email)

    def add_price_variation(self, price_variation):
        self.price_variations.append(price_variation)

    def parse_trigger(self, trigger_text):

        matches = TrackedProduct.percentageMatcher.search(trigger_text).group()

        if matches is not None:
            return self.relative_variation(int(matches[0]))
        else:
            if trigger_text.startsWith('<'):
                return self.absolute_variation(-int(trigger_text[:1]))
            else:
                return self.absolute_variation(int(trigger_text[:1]))

    def relative_variation(self, variation):

        def calculate(prev_price, new_price):
            percentage_diff = (new_price / prev_price * 100) - 100;

            if variation < 0:
                return percentage_diff <= variation
            else:
                return percentage_diff > variation

        return calculate

    def absolute_variation(self, variation):

        def calculate(new_price):
            if variation < 0:
                return new_price <= variation
            else:
                return new_price > variation

        return calculate

    def json_encoder(self):

        pass

    def json_decoder(self, obj):
        return TrackedProduct(obj['id'],
                              obj['name'],
                              obj['url'],
                              obj['price_selector'],
                              [self.parse_trigger(trigger) for trigger in obj['triggers']],
                              obj['emails_to_notify'],
                              obj['monitor_interval'],
                              [])


##########################################################

class PriceVariation(object):

    def __init__(self, date, previous_price, current_price):
        self.date = date
        self.previous_price = previous_price
        self.current_price = current_price

##########################################################

def main(argv):
    # My code here
    pass

if __name__ == "__main__":
    main(sys.argv)
    product1 = TrackedProduct(1, "Item", "www.amazon.es", "p.price > li", 32000)
    jsonProd1 = json.dumps(product1.__dict__)
    print(jsonProd1)
