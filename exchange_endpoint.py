from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from algosdk import mnemonic
from algosdk import account
from algosdk.v2client import indexer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback


from web3 import Web3

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()

    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True

    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')

    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True

    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()


""" End of pre-defined methods """

""" Helper Methods (skeleton code for you to implement) """


def log_message(message_dict):
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    g.session.add(Log(message=msg))
    g.session.commit()

    return


def get_algo_keys():
    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys
    private_key = "UXsliYj/em52Okvg+/hy/amUYuTnJ0MGaP6aSYwaAYlfCBnqsm1nYN32B+W8LO8fOipqvsTsz+bI/LYVKU7zGA=="
    public_address = "L4EBT2VSNVTWBXPWA7S3YLHPD45CU2V6YTWM7ZWI7S3BKKKO6MMAPKJKJI"

    mnemonic_secret = mnemonic.from_private_key(private_key)
    algo_sk = mnemonic.to_private_key(mnemonic_secret)
    algo_pk = mnemonic.to_public_key(mnemonic_secret)

    return algo_sk, algo_pk


def get_eth_keys(filename="eth_mnemonic.txt"):
    #w3 = Web3()

    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    w3 = connect_to_eth()
    w3.eth.account.enable_unaudited_hdwallet_features()
    #mnemonic_secret = "axis fence motion nest plastic skirt expand voyage story inquiry wealth gloom"
    #with open(filename, "r") as f:
    mnemonic_secret = "initial chair key two unhappy liquid scissors fold swift relax custom resource"
    account = w3.eth.account.from_mnemonic(mnemonic_secret)
    eth_pk = account.address
    eth_sk = account.private_key

    return eth_sk, eth_pk

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
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!

    matched_ord = match_order(order)
    if (matched_ord != None):
        current_time = datetime.now()
        matched_ord.filled = current_time
        order.filled = current_time
        matched_ord.counterparty_id = order.id
        order.counterparty_id = matched_ord.id
        g.session.commit()

        # add to the list and execute
        amount1 = math.ceil(min(order.buy_amount, matched_ord.sell_amount))
        amount2 = math.ceil(min(matched_ord.buy_amount, order.sell_amount))
        tx1 = {'amount': amount1,
               'platform': order.buy_currency,
               'order_id': order.id,
               'order': order,
               'receiver_pk': order.receiver_pk}
        tx2 = {'amount': amount2,
               'platform': matched_ord.buy_currency,
               'order_id': matched_ord.id,
               'order': matched_ord,
               'receiver_pk': matched_ord.receiver_pk}
        txes.append(tx1)
        txes.append(tx2)
        execute_txes(txes)

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
                                     math.ceil(buy_amount * matched_ord.sell_amount / matched_ord.buy_amount))
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


def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print(f"Trying to execute {len(txes)} transactions")
    print(f"IDs = {[tx['order_id'] for tx in txes]}")
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    if not all(tx['platform'] in ["Algorand", "Ethereum"] for tx in txes):
        print("Error: execute_txes got an invalid platform!")
        print(tx['platform'] for tx in txes)

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand"]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum"]

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    algo_tx_id = send_tokens_algo(g.acl, algo_sk, algo_txes)
    eth_tx_id = send_tokens_eth(g.w3, eth_sk, eth_txes)

    for tx in algo_tx_id:
        tx_obj = TX(platform=tx['platform'],
                    receiver_pk=tx['receiver_pk'],
                    order_id=tx['order_id'],
                    order=tx['order'],
                    tx_id=tx['tx_id'])
        g.session.add(tx_obj)
        g.session.commit()

    for tx in eth_tx_id:
        tx_obj = TX(platform=tx['platform'],
                    receiver_pk=tx['receiver_pk'],
                    order_id=tx['order_id'],
                    order=tx['order'],
                    tx_id=tx['tx_id'])
        g.session.add(tx_obj)
        g.session.commit()

def obj_to_dict(order):
    res_dict = {}
    res_dict['sender_pk'] = order.sender_pk
    res_dict['receiver_pk'] = order.receiver_pk
    res_dict['buy_currency'] = order.buy_currency
    res_dict['sell_currency'] = order.sell_currency
    res_dict['buy_amount'] = order.buy_amount
    res_dict['sell_amount'] = order.sell_amount
    res_dict['signature'] = order.signature
    res_dict['tx_id'] = order.tx_id
    return res_dict

""" End of Helper methods"""


@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print(f"Error: no platform provided")
            return jsonify("Error: no platform provided")
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print(f"Error: {content['platform']} is an invalid platform")
            return jsonify(f"Error: invalid platform provided: {content['platform']}")

        if content['platform'] == "Ethereum":
            # Your code here
            eth_sk, eth_pk = get_eth_keys()
            return jsonify(eth_pk)
        if content['platform'] == "Algorand":
            # Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify(algo_pk)


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade", file=sys.stderr)
    connect_to_blockchains()
    #get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = ["buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        # Your code here

        # 1. Check the signature

        # 2. Add the order to the table

        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)

        # 3b. Fill the order (as in Exchange Server II) if the order is valid

        # 4. Execute the transactions

        # If all goes well, return jsonify(True). else return jsonify(False)
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
                                  signature=content['sig'],
                                  tx_id=payload['tx_id'])
                g.session.add(order_obj)
                g.session.commit()

                tx = g.w3.eth.get_transaction(payload['tx_id'])
                #eth_sk, eth_pk = get_eth_keys()
                if tx['from'] != payload['sender_pk'] or tx['to'] != payload['receiver_pk'] or tx['value'] != payload['sell_amount']:
                    return jsonify(False)
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
                                  signature=content['sig'],
                                  tx_id = payload['tx_id'])
                g.session.add(order_obj)
                g.session.commit()
                try:
                    temp = connect_to_algo(connection_type='indexer')
                    response = temp.search_transactions(txid=payload['tx_id'])
                    if len(response["transactions"]) > 0:
                        #algo_sk, algo_pk = get_algo_keys()
                        if (response["transactions"]["sender"] != payload['sender_pk'] or
                                response["transactions"]["payment-transaction"]["receiver"] != payload['receiver_pk'] or
                                response["transactions"]["payment-transaction"]["amount"] != payload[
                                    'sell_amount']):
                            return jsonify(False)
                        fill_order(order_obj)
                except:
                    print(traceback.format_exc())
                    return jsonify(False)

            else:
                log_message(json.dumps(content['payload']))
        return jsonify(True)


@app.route('/order_book')
def order_book():


    # Same as before
    fields = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id"]

    result = {'data': []}
    orders = g.session.query(Order)
    for order in orders:
        result['data'].append(obj_to_dict(order))
    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
