from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# 检查连接
print(w3.isConnected())

# 获取最新区块号
print(w3.eth.block_number)

# 使用与私钥匹配的地址
sender_address = '0x705C448d2c1c753845498040847C8Ed9e2522F3e'
print(sender_address)

print(w3.eth.mining)

# 获取当前的 chain_id
chain_id = w3.eth.chain_id

# 构建交易
tx = {
    'from': sender_address,
    'to': w3.toChecksumAddress('0xe136eADEd3e05D98CeFd285E82F173C3132703C5'),  # 接收者地址
    'value': w3.toWei(0.1, 'ether'),
    'gas': 2000000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(sender_address),
    'chainId': chain_id  # 添加 chain_id 以启用 EIP-155 重放保护
}

# 发送交易
try:
    # 签名交易
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='0x739fbd2341afef96bc9eb223c2bb7a657f66093faf848c2e3794a24990e77c98')
    # 发送已签名的交易
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"交易发送成功，交易哈希：{tx_hash.hex()}")
except Exception as e:
    print(f"交易失败：{e}")
