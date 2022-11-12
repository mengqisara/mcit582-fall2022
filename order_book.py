import math
from random import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

platforms = ["Algorand", "Ethereum"]
platform = "Ethereum"
sender_pk = hex(random.randint(0,2**256))[2:] #Generate random string that looks like a public key
receiver_pk = hex(random.randint(0,2**256))[2:] #Generate random string that looks like a public key

other_platform = platforms[1-platforms.index(platform)]

def insert_order(order):
    fields = ['sender_pk', 'receiver_pk', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount']
    order_res = Order(**{f: order[f] for f in fields})

    session.add(order_res)
    session.commit()
    return order_res


def match_order(order):
    max_profit = 0
    matched_order = None
    orders = session.query(Order).filter(Order.filled == None, Order.buy_currency == order.sell_currency,
                                           Order.sell_currency == order.buy_currency).all()
    for o in orders:
        if order.buy_amount / order.sell_amount < o.sell_amount / o.buy_amount and o.sell_amount / o.buy_amount - order_rate > max_profit:
            max_profit = o.sell_amount / o.buy_amount - order.buy_amount / order.sell_amount

            matched_order = o

    return matched_order

def create_child(order_obj, buy_amount, sell_amount):
    child_order = {}
    child_order['sender_pk'] = order_obj.sender_pk
    child_order['receiver_pk'] = order_obj.receiver_pk
    child_order['buy_currency'] = order_obj.buy_currency
    child_order['sell_currency'] = order_obj.sell_currency
    child_order['buy_amount'] = buy_amount
    child_order['sell_amount'] = sell_amount
    child_order['creator_id'] = order_obj.id
    child_order['tx_id'] = order_obj.tx_id
    insert_order(child_order)
    session.commit()
    return child_order

def fill_order(order_res):
    matched_ord = match_order(order_res)
    if (matched_ord != None):
        current_time = datetime.now()
        matched_ord.filled = current_time
        order_res.filled = current_time
        matched_ord.counterparty_id = order_res.id
        order_res.counterparty_id = matched_ord.id
        session.commit()


        if order_res.buy_amount > matched_ord.sell_amount:
            buy_amount = order_res.buy_amount - matched_ord.sell_amount
            child_ord = create_child(order_res, buy_amount, math.ceil(buy_amount*order_res.sell_amount / order_res.buy_amount))
            fill_order(child_ord)
        if matched_ord.buy_amount > order_res.sell_amount:  # create child order for match order
            buy_amount = matched_ord.buy_amount - order_res.sell_amount
            child_ord = create_child(matched_ord, buy_amount, math.ceil(buy_amount / (matched_ord.buy_amount / matched_ord.sell_amount)))
            fill_order(child_ord)

    session.commit()

    return

def process_order(order):
    #Your code here
    order_res = insert_order(order)
    matched_order=match_order(order)
    fill_order(order_res)
    pass


