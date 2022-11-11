#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk.future.transaction import PaymentTxn

#pri_key, pub_address = account.generate_account()

#mnemonic_pri_key = mnemonic.from_private_key(pri_key)



#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

public_address = 'EXRLTVWLVJNEBOTRMZEWHIKM2BBKPOS6DTRQ727P5R4MHTCQTZMT6D4J74'
mnemonic_pri_key = "world broom ensure remove burger deer thrive unable cage thrive sea wrong snake judge flip genuine forest garlic much business lecture fine sugar abandon tortoise"


def send_tokens( receiver_pk, tx_amount ):
    params = acl.suggested_params()
    gen_hash = params.gh
    first_valid_round = params.first
    tx_fee = params.min_fee
    last_valid_round = params.last

    #Your code here
    #generate transaction
    txn_unsigned = PaymentTxn(public_address, params, receiver_pk, tx_amount, None)
    #sign the transaction
    txn_sign = txn_unsigned.sign(mnemonic.to_private_key(mnemonic_pri_key))
    #submit transaction
    txid = acl.send_transaction(txn_sign)

    sender_pk = public_address
    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo
