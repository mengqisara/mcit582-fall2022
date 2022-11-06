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
    cont = json.dumps(content)
    platform = cont['payload']['platform']
    print(platform)
    sign = cont['sig']
    print(sign)
    payload = cont['payload']
    msg = payload['message']
    print(msg)
    result: bool
    try:
        if (platform == 'Ethereum'):
            #eth_account.Account.enable_unaudited_hdwallet_features()
            #acct, mnemonic = eth_account.Account.create_with_mnemonic()

            eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
            if eth_account.Account.recover_message(eth_encoded_msg, signature=sign) == payload['pk']:
                result = True
                print('Eth verify:True')
            else:
                result = False
                print('Eth verify:False')

        else:
            #algo_sk, algo_pk = algosdk.account.generate_account()

            # BYTE_ARRAY = bytearray.fromhex(int(sign,16))
            # algo_sig_str = base64.b64encode(BYTE_ARRAY)

            if algosdk.util.verify_bytes(msg.encode('utf-8'), sign, payload['pk']):
                result = True
                print('Algo verify:True')
            else:
                result = False
                print('Algo verify:False')
    except Exception as e:
        import traceback
        print(traceback.format_exc())

    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
