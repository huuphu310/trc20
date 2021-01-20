from sanic import Sanic
from sanic_healthcheck import HealthCheck
from sanic.response import json
from tronapi import Tron
import random

app = Sanic("trc20")
health_check = HealthCheck(app)


# Define checks for the health check.
def check_health_random():
    if random.random() > 0.9:
        return False, 'the random number is > 0.9'
    return True, 'the random number is <= 0.9'

def send_from_to(from_addr, to_addr, private_key, contract_addr, send_value, fee_limit):
    full_node = 'https://api.trongrid.io'
    solidity_node = 'https://api.trongrid.io'
    event_server = 'https://api.trongrid.io'

    Tron(full_node=full_node,
         solidity_node=solidity_node,
         event_server=event_server)

    trx_kwargs = dict()
    trx_kwargs["private_key"] = private_key
    trx_kwargs["default_address"] = from_addr

    tron = Tron(**trx_kwargs)

    kwargs = dict()
    kwargs["contract_address"] = contract_addr
    kwargs["function_selector"] = "transfer(address,uint256)"
    kwargs["fee_limit"] = fee_limit
    kwargs["call_value"] = 0
    kwargs["parameters"] = [
        {
            'type': 'address',
            'value': to_addr
        },
        {
            'type': 'uint256',
            'value': send_value
        }
    ]

    raw_tx = tron.transaction_builder.trigger_smart_contract(**kwargs)
    sign = tron.trx.sign(raw_tx["transaction"])
    result = tron.trx.broadcast(sign)

    return result


@app.route("/send_from_to", methods=['POST'])
def post_json(request):
    request_received = request.json
    from_addr = request_received.get('from_addr')
    to_addr = request_received.get('to_addr')
    private_key = request_received.get('private_key')
    contract_addr = request_received.get('contract_addr')
    send_value = request_received.get('send_value')
    if request_received.get('fee_limit2') is None:
        fee_limit = 2000000
    else:
        fee_limit = request_received.get('fee_limit')
    response = send_from_to(from_addr, to_addr, private_key, contract_addr, send_value, fee_limit)
    return json(response)


if __name__ == "__main__":
    health_check.add_check(check_health_random)
    app.run(host="0.0.0.0", port=8000)
