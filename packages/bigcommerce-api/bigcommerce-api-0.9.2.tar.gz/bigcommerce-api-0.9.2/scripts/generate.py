import random, string, sys, datetime, time
from email import Utils
import bigcommerce as api
import settings

try:
    to_gen_customers = int(sys.argv[1])
    to_gen_orders = int(sys.argv[2])
except:
    print "Usage: ./whateverimcalled num_customers_to_make num_orders_to_make"
    sys.exit(1)

client = api.OAuthConnection(settings.CLIENT_ID, settings.STORE_HASH,
                             host=settings.API_PROXY, access_token=settings.ACCESS_TOKEN)

# random customers

def r_email(N=10): 
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(N)) + '@gmail.com'

names = ['John', 'Jane', 'Lee', 'Tal', 'Homu', 'Homer', 'Zebra', 'Contul']
lnames = ['Hippo', 'Red', 'Onny', 'McHam', 'Cheeseburger', 'Action', 'Gold']


def gen_customers(N=10): # might be good to add store credit
    """Returns a list of created customer IDs, first/last names, and emails"""
    print "Generating customers"
    customers = []
    i = 0
    M = 0
    while i < N:
        print " ."
        try:
            data = {'first_name' : random.choice(names),
                    'last_name' : random.choice(lnames),
                    'email' : r_email()}
            res = client.create('customers', data)
            customers.append( (res['id'], res['first_name'], res['last_name'], res['email']) )
            i += 1
            print ". "
        except Exception as e:
            M += 1
            if isinstance(e, api.HttpException):
                print e
                print e.response.request.body
            if M > 20:
                print "You might be trying too hard. Please take a break."
                raise
    return customers


# random orders 

# can't be bothered with mandatory options
# so get list of products without them
def no_option_products(stop_at=4):
    no_op_products = []
    product_ids = [prod['id'] for prod in client.get('products')]
    for pi in product_ids:
        ops_required = False
        try:
            options = client.get('products/{}/options'.format(pi))
            for op in options:
                if op['is_required'] == True: ops_required = True
        except api.EmptyResponseWarning:
            pass
        finally:
            if not ops_required: no_op_products.append(pi)
        if len(no_op_products) >= stop_at:
            return no_op_products
    return no_op_products

def gen_orders(N=20):
    print "Generating random orders"
    i=0
    M = 0
    noopr = no_option_products()
    while i < N:
        print " ."
        try: # if it dies it should be because bad randomised data
            order_data = {
                "billing_address": {
                    "company": "",
                    "street_1": "12345 W Anderson Ln",
                    "street_2": "",
                    "city": "Austin",
                    "state": "Texas",
                    "zip": "78757",
                    "country": "United States",
                    "country_iso2": "US",
                    "phone": ""
                },
            }
            
            randude = random.choice(customers)
            # SUPPORT ISO PLEASE
#             year = random.choice(range(2005, 2013))
#             month = random.choice(range(1, 12))
#             day = random.choice(range(1, 28))
#             randate = datetime.datetime(year, month, day).isoformat()

            now = datetime.datetime.now()

            # random time in the past half year?
            year = 0 #random.randint(0, 1)
            month = random.randint(0, 5)
            day = random.randint(0, 30)
            days = (year * 365) + (month * 30) + day
            
            randatetime = now - datetime.timedelta(days = days)

            tuple = randatetime.timetuple()
            timestamp = time.mktime(tuple)
            randate = Utils.formatdate(timestamp)

            random_data = {"customer_id" : randude[0],
                           "status_id" : random.randint(1, 11),
                           "date_created" : randate,
                           "products" : []
                           }
            
            billing_data = {
                    "first_name" : randude[1],
                    "last_name": randude[2],
                    "email" : randude[3]
                    }
            
            order_products = []
            for _ in range(random.randint(1, 4)):
                order_products.append({"product_id" : random.choice(noopr),
                                       "quantity" : random.randint(1, 10)})
            random_data['products'] = order_products
            
            order_data.update(random_data)
            order_data['billing_address'].update(billing_data)
            
            res = client.create('/orders', order_data)
            i += 1
            print ". "
        except Exception as e:  # CANT BE BOTHERED WITH THE RIGHT EXCEPTION
            M += 1
            print e
            if M > 20:
                print "You might be trying too hard. Please take a break."
                raise

client.timeout = 15.0

try:
    customers = gen_customers(to_gen_customers)
    # grab the customers again, so orders get spread among existing ones too
    customers = [ (res['id'], res['first_name'], res['last_name'], res['email']) for res in client.get('customers') ]

    gen_orders(to_gen_orders)
    print "Done"
except Exception as e:  # almost certainly will be a 509
    try:
        if e.status_code == 509:
            print "Reached request limit somehow. Try running the script later?"
        else:
            print e
    except:
        pass
    raise

