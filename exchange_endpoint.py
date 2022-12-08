import math

from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """


def check_sig(payload, sig):
    sender_pk = payload['sender_pk']
    if payload.get('platform') == 'Ethereum':
        encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        return eth_account.Account.recover_message(encoded_msg, signature=sig) == sender_pk
    else:
        return algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk)


def insert_order(order):
    fields = ['sender_pk', 'receiver_pk', 'buy_currency', 'sell_currency', 'buy_amount', 'sell_amount']
    order_res = Order(**{f: order[f] for f in fields})

    g.session.add(order_res)
    g.session.commit()
    return order_res

def match_order(order):
    max_profit = 0
    matched_order = None
    orders = g.session.query(Order).filter(Order.filled == None, Order.buy_currency == order.sell_currency,
                                           Order.sell_currency == order.buy_currency).all()
    for o in orders:
        if order.buy_amount / order.sell_amount < o.sell_amount / o.buy_amount and o.sell_amount / o.buy_amount - order.buy_amount / order.sell_amount > max_profit:
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
    child_order_res=insert_order(child_order)
    g.session.commit()
    return child_order_res

def fill_order(order, txes=[]):
    matched_ord = match_order(order)
    if (matched_ord != None):
        current_time = datetime.now()
        matched_ord.filled = current_time
        order.filled = current_time
        matched_ord.counterparty_id = order.id
        order.counterparty_id = matched_ord.id
        g.session.commit()

        if order.buy_amount > matched_ord.sell_amount:
            buy_amount = order.buy_amount - matched_ord.sell_amount
            child_ord = create_child(order, buy_amount,
                                     math.ceil(buy_amount * order.sell_amount / order.buy_amount))
            child_list = []
            if order.child == None:
                child_list.append(child_ord)
                order.child = child_list
            elif order.child != None:
                child_list = order.child
                child_list.append(child_ord)
                order.child = child_list
            fill_order(child_ord)
        if matched_ord.buy_amount > order.sell_amount:
            buy_amount = matched_ord.buy_amount - order.sell_amount
            child_ord = create_child(matched_ord, buy_amount,
                                     math.ceil(buy_amount / (matched_ord.buy_amount / matched_ord.sell_amount)))
            child_list = []
            if matched_ord.child == None:
                child_list.append(child_ord)
                matched_ord.child = child_list
            elif matched_ord.child != None:
                child_list = matched_ord.child
                child_list.append(child_ord)
                matched_ord.child = child_list
            fill_order(child_ord)

    g.session.commit()
    return


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    msg = json.dumps(d)
    g.session.add(Log(message=msg))
    g.session.commit()
    return

def obj_to_dict(order):
    res_dict = {}
    res_dict['sender_pk'] = order.sender_pk
    res_dict['receiver_pk'] = order.receiver_pk
    res_dict['buy_currency'] = order.buy_currency
    res_dict['sell_currency'] = order.sell_currency
    res_dict['buy_amount'] = order.buy_amount
    res_dict['sell_amount'] = order.sell_amount
    res_dict['signature'] = order.signature
    return res_dict

""" End of helper methods """


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
        fields = ["sig", "payload"]

        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session

        # TODO: Check the signature


        # TODO: Add the order to the database

        # TODO: Fill the order

        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        payload = content['payload']
        if content['payload']['platform'] == 'Ethereum':
            result = check_sig(content['payload'], content['sig'])
            if result:
                order_obj = Order(sender_pk=payload['sender_pk'],
                                  receiver_pk=payload['receiver_pk'],
                                  buy_currency=payload['buy_currency'],
                                  sell_currency=payload['sell_currency'],
                                  buy_amount=payload['buy_amount'],
                                  sell_amount=payload['sell_amount'],
                                  signature=content['sig'])
                g.session.add(order_obj)
                g.session.commit()
                fill_order(order_obj)

            else:
                log_message(json.dumps(content['payload']))

        if content['payload']['platform'] == 'Algorand':
            result = check_sig(content['payload'], content['sig'])
            if result:
                order_obj = Order(sender_pk=payload['sender_pk'],
                                  receiver_pk=payload['receiver_pk'],
                                  buy_currency=payload['buy_currency'],
                                  sell_currency=payload['sell_currency'],
                                  buy_amount=payload['buy_amount'],
                                  sell_amount=payload['sell_amount'],
                                  signature=content['sig'])
                g.session.add(order_obj)
                g.session.commit()
                fill_order(order_obj)

            else:
                log_message(json.dumps(content['payload']))

        return jsonify(True)


@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
    fields = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature"]

    result = {'data': []}
    orders = g.session.query(Order)
    for order in orders:
        result['data'].append(obj_to_dict(order))
    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
