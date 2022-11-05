import base64

from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk
from hexbytes import HexBytes
from werkzeug.debug import console

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)
    cont = json.loads(json.dumps(content))
    platform = cont['payload']['platform']
    print(platform)
    console.log(platform)
    sign = cont['sig']
    print(sign)
    console.log(sign)
    payload = cont['payload']
    msg = payload['message']
    print(msg)
    console.log(msg)
    result: bool
    if(platform=='Ethereum'):
        eth_account.Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = eth_account.Account.create_with_mnemonic()

        eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
        if eth_account.Account.recover_message(eth_encoded_msg,signature='0x3718eb506f445ecd1d6921532c30af84e89f2faefb17fc8117b75c4570134b4967a0ae85772a8d7e73217a32306016845625927835818d395f0f65d25716356c1c') == payload['pk']:
            result = True
            print('Eth verify:True')
        else:
            result = False
            print('Eth verify:False')

    else:
        algo_sk, algo_pk = algosdk.account.generate_account()

        BYTE_ARRAY = bytearray.fromhex(hex(int(sign,16)))
        algo_sig_str = base64.b64encode(BYTE_ARRAY)

        if algosdk.util.verify_bytes(msg.encode('utf-8'), algo_sig_str, payload['pk']):
            result = True
            print('Algo verify:True')
        else:
            result = False
            print('Algo verify:False')
            

    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')


python3 .guides/mcit582-fall2022/verification_endpoint.py
