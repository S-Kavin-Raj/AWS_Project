import boto3
import uuid
import os
from decimal import Decimal
from datetime import datetime, date

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID', 'testing')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'testing')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

dynamodb = session.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)
dynamodb_client = session.client('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)

USER_TABLE = 'stocker_users'
STOCK_TABLE = 'stocker_stocks'
TRANSACTION_TABLE = 'stocker_transactions'
PORTFOLIO_TABLE = 'stocker_portfolio'

existing_tables = dynamodb_client.list_tables()['TableNames']

def create_table_if_not_exists(table_name, key_schema, attribute_definitions):
    if table_name not in existing_tables:
        print(f"Creating table: {table_name}")
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            BillingMode='PAY_PER_REQUEST'
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created!")
    else:
        print(f"Table {table_name} already exists.")

create_table_if_not_exists(USER_TABLE,
    [{'AttributeName': 'email', 'KeyType': 'HASH'}],
    [{'AttributeName': 'email', 'AttributeType': 'S'}])
create_table_if_not_exists(STOCK_TABLE,
    [{'AttributeName': 'id', 'KeyType': 'HASH'}],
    [{'AttributeName': 'id', 'AttributeType': 'S'}])
create_table_if_not_exists(TRANSACTION_TABLE,
    [{'AttributeName': 'id', 'KeyType': 'HASH'}],
    [{'AttributeName': 'id', 'AttributeType': 'S'}])
create_table_if_not_exists(PORTFOLIO_TABLE,
    [{'AttributeName': 'user_id', 'KeyType': 'HASH'}, {'AttributeName': 'stock_id', 'KeyType': 'RANGE'}],
    [{'AttributeName': 'user_id', 'AttributeType': 'S'}, {'AttributeName': 'stock_id', 'AttributeType': 'S'}])

# ---- USERS ----
trader1_id = str(uuid.uuid4())
trader2_id = str(uuid.uuid4())
users = [
    {'id': str(uuid.uuid4()), 'username': 'Admin User',   'email': 'admin@example.com',   'password': 'admin123',  'role': 'admin'},
    {'id': trader1_id,        'username': 'Trader One',  'email': 'trader1@example.com', 'password': 'trader123', 'role': 'trader'},
    {'id': trader2_id,        'username': 'Trader Two',  'email': 'trader2@example.com', 'password': 'trader123', 'role': 'trader'},
]
user_table = dynamodb.Table(USER_TABLE)
with user_table.batch_writer() as batch:
    for u in users:
        batch.put_item(Item=u)
print("Users added.")

# ---- STOCKS ----
today = date.today().isoformat()
stocks_data = [
    ("RELIANCE","Reliance Industries Ltd","2500.00","1700000","Energy","Oil & Gas"),
    ("TCS","Tata Consultancy Services Ltd","3600.00","1300000","IT","IT Services"),
    ("HDFCBANK","HDFC Bank Ltd","1600.00","1100000","Financials","Bank"),
    ("ICICIBANK","ICICI Bank Ltd","1100.00","800000","Financials","Bank"),
    ("INFY","Infosys Ltd","1500.00","700000","IT","IT Services"),
    ("HINDUNILVR","Hindustan Unilever Ltd","2500.00","650000","Consumer Goods","FMCG"),
    ("ITC","ITC Ltd","450.00","550000","Consumer Goods","FMCG"),
    ("KOTAKBANK","Kotak Mahindra Bank Ltd","1700.00","450000","Financials","Bank"),
    ("LT","Larsen & Toubro Ltd","3300.00","400000","Industrials","Construction"),
    ("SBIN","State Bank of India","750.00","380000","Financials","Bank"),
    ("BHARTIARTL","Bharti Airtel Ltd","1000.00","350000","Communication","Telecom"),
    ("BAJFINANCE","Bajaj Finance Ltd","7000.00","300000","Financials","NBFC"),
    ("ASIANPAINT","Asian Paints Ltd","3200.00","250000","Consumer Goods","Paints"),
    ("AXISBANK","Axis Bank Ltd","1000.00","240000","Financials","Bank"),
    ("HCLTECH","HCL Technologies Ltd","1600.00","230000","IT","IT Services"),
    ("MARUTI","Maruti Suzuki India Ltd","12000.00","220000","Consumer Goods","Automobiles"),
    ("SUNPHARMA","Sun Pharmaceutical Industries Ltd","1300.00","210000","Healthcare","Pharma"),
    ("BAJAJFINSV","Bajaj Finserv Ltd","1700.00","200000","Financials","NBFC"),
    ("TITAN","Titan Company Ltd","3500.00","195000","Consumer Goods","Luxury Goods"),
    ("ULTRACEMCO","UltraTech Cement Ltd","9000.00","180000","Industrials","Cement"),
    ("NTPC","NTPC Ltd","300.00","170000","Utilities","Power"),
    ("POWERGRID","Power Grid Corporation of India Ltd","250.00","160000","Utilities","Power"),
    ("ADANIENT","Adani Enterprises Ltd","3100.00","150000","Conglomerate","Diversified"),
    ("JSWSTEEL","JSW Steel Ltd","900.00","140000","Materials","Steel"),
    ("TATASTEEL","Tata Steel Ltd","150.00","130000","Materials","Steel"),
    ("HDFCLIFE","HDFC Life Insurance Company Ltd","600.00","120000","Financials","Insurance"),
    ("TECHM","Tech Mahindra Ltd","1200.00","115000","IT","IT Services"),
    ("WIPRO","Wipro Ltd","600.00","110000","IT","IT Services"),
    ("BRITANNIA","Britannia Industries Ltd","5000.00","100000","Consumer Goods","FMCG"),
    ("CIPLA","Cipla Ltd","1200.00","95000","Healthcare","Pharma"),
    ("DIVISLAB","Divi's Laboratories Ltd","3700.00","90000","Healthcare","Pharma"),
    ("GRASIM","Grasim Industries Ltd","2200.00","85000","Materials","Cement"),
    ("BPCL","Bharat Petroleum Corporation Ltd","550.00","80000","Energy","Oil & Gas"),
    ("ONGC","Oil and Natural Gas Corporation Ltd","250.00","75000","Energy","Oil & Gas"),
    ("ADANIPORTS","Adani Ports and Special Economic Zone Ltd","1200.00","70000","Industrials","Logistics"),
    ("DRREDDY","Dr. Reddy's Laboratories Ltd","5700.00","65000","Healthcare","Pharma"),
    ("HINDALCO","Hindalco Industries Ltd","650.00","60000","Materials","Aluminium"),
    ("INDUSINDBK","IndusInd Bank Ltd","1400.00","58000","Financials","Bank"),
    ("EICHERMOT","Eicher Motors Ltd","4000.00","56000","Consumer Goods","Automobiles"),
    ("HEROMOTOCO","Hero MotoCorp Ltd","3200.00","54000","Consumer Goods","Automobiles"),
    ("APOLLOHOSP","Apollo Hospitals Enterprise Ltd","5400.00","50000","Healthcare","Hospitals"),
    ("SBILIFE","SBI Life Insurance Company Ltd","1400.00","48000","Financials","Insurance"),
    ("ICICIPRULI","ICICI Prudential Life Insurance Company Ltd","550.00","46000","Financials","Insurance"),
    ("TATACONSUM","Tata Consumer Products Ltd","900.00","44000","Consumer Goods","FMCG"),
    ("UPL","UPL Ltd","600.00","42000","Materials","Agro Chemicals"),
    ("COALINDIA","Coal India Ltd","300.00","40000","Materials","Mining"),
    ("SHREECEM","Shree Cement Ltd","27000.00","38000","Industrials","Cement"),
    ("BAJAJ-AUTO","Bajaj Auto Ltd","5000.00","36000","Consumer Goods","Automobiles"),
]
stock_ids = {}
stocks = []
for sym, name, price, mcap, sector, industry in stocks_data:
    sid = str(uuid.uuid4())
    stock_ids[sym] = sid
    stocks.append({'id': sid, 'symbol': sym, 'name': name, 'price': Decimal(price),
                   'market_cap': Decimal(mcap), 'sector': sector, 'industry': industry, 'date_added': today})

stock_table = dynamodb.Table(STOCK_TABLE)
with stock_table.batch_writer() as batch:
    for s in stocks:
        batch.put_item(Item=s)
print(f"All {len(stocks)} stocks added.")

# ---- TRANSACTIONS & PORTFOLIO ----
now = datetime.now().isoformat()
transaction_table = dynamodb.Table(TRANSACTION_TABLE)
portfolio_table = dynamodb.Table(PORTFOLIO_TABLE)

sample_txns = [
    {'id': str(uuid.uuid4()), 'user_id': trader1_id, 'stock_id': stock_ids['RELIANCE'],
     'action': 'buy', 'quantity': 10, 'price': Decimal('2500.00'), 'status': 'completed', 'transaction_date': now},
    {'id': str(uuid.uuid4()), 'user_id': trader1_id, 'stock_id': stock_ids['TCS'],
     'action': 'buy', 'quantity': 5,  'price': Decimal('3600.00'), 'status': 'completed', 'transaction_date': now},
    {'id': str(uuid.uuid4()), 'user_id': trader2_id, 'stock_id': stock_ids['HDFCBANK'],
     'action': 'buy', 'quantity': 15, 'price': Decimal('1600.00'), 'status': 'completed', 'transaction_date': now},
]
with transaction_table.batch_writer() as batch:
    for t in sample_txns:
        batch.put_item(Item=t)

portfolio_items = [
    {'user_id': trader1_id, 'stock_id': stock_ids['RELIANCE'], 'quantity': 10, 'average_price': Decimal('2500.00')},
    {'user_id': trader1_id, 'stock_id': stock_ids['TCS'],      'quantity': 5,  'average_price': Decimal('3600.00')},
    {'user_id': trader2_id, 'stock_id': stock_ids['HDFCBANK'], 'quantity': 15, 'average_price': Decimal('1600.00')},
]
with portfolio_table.batch_writer() as batch:
    for p in portfolio_items:
        batch.put_item(Item=p)

print("Transactions and portfolios added.")
print("DynamoDB setup completed successfully!")
