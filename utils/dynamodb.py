from django.conf import settings

from boto import dynamodb
from boto.dynamodb.condition import BETWEEN


def get_conn():
    return dynamodb.connect_to_region(
        'us-east-1', 
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

def get_item(hash_key, range_start, range_end):
    conn = get_conn()
    table = conn.get_table(settings.DYNAMODB_TABLE)
    return list(table.query(
        hash_key=hash_key, 
        range_key_condition=BETWEEN(
            range_start, 
            range_end,
        ),
    ))

def write_items(conn, table, items):
    batch = dynamodb.batch.BatchWriteList(conn)
    batch.add_batch(table, puts=items)
    return conn.batch_write_item(batch)

def get_items(conn, table, keys):
    batch = dynamodb.batch.BatchList(conn)
    batch.add_batch(table, keys)
    return conn.batch_get_item(batch)
