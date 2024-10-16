from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# 检查连接
print(w3.is_connected())

# 获取最新区块号
print(w3.eth.block_number)

# 获取账户列表
print(w3.eth.accounts)