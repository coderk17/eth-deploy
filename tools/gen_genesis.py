"""
此文件用于生成以太坊创世区块配置文件。

主要功能:
1. 创建指定数量的账户
2. 生成创世区块配置，包括PoW和PoS两种共识机制
3. 为每个账户分配随机数量的初始余额

使用方法:
1. 调用create_accounts()函数创建账户
2. 调用create_genesis()函数生成创世区块配置
3. 根据需要选择PoW或PoS共识机制
"""
import json
import os
import random

from eth_account import Account

def create_accounts(num_accounts=100):
    accounts = []
    for _ in range(num_accounts):
        new_account = Account.create()
        accounts.append({
            "address": new_account.address,
            "private_key": new_account.privateKey.hex()
        })
    return accounts

def create_genesis(accounts, is_pos=False):
    genesis = {
        "config": {
            "chainId": 193284561987324,
            "homesteadBlock": 0,
            "eip150Block": 0,
            "eip155Block": 0,
            "eip158Block": 0,
            "byzantiumBlock": 0,
            "constantinopleBlock": 0,
            "petersburgBlock": 0,
            "istanbulBlock": 0,
            "berlinBlock": 0,
            "londonBlock": 0
        },
        "difficulty": "1",
        "gasLimit": "8000000",
        "alloc": {}
    }

    if is_pos:
        genesis["config"]["clique"] = {
            "period": 15,
            "epoch": 30000
        }
        # 选择第一个账户作为初始验证者
        genesis["extradata"] = "0x" + "0" * 64 + accounts[0]["address"][2:] + "0" * 130
    else:
        genesis["config"]["ethash"] = {}

    for account in accounts:
        initial_balance = random.randint(100000, 200000)
        wei_balance = str(initial_balance * 10**18)  # 转换为wei
        genesis["alloc"][account["address"]] = {"balance": wei_balance}

    return genesis

def main():
    # 创建data目录（如果不存在）
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/pow', exist_ok=True)
    os.makedirs('data/pos', exist_ok=True)

    # 生成100个账户
    accounts = create_accounts()

    # 将账户信息保存到accounts.json文件
    with open('data/accounts.json', 'w') as f:
        json.dump(accounts, f, indent=2)

    print(f"已生成100个账户并保存到 data/accounts.json")

    # 创建PoW版本的genesis.json
    pow_genesis = create_genesis(accounts, is_pos=False)
    with open('data/pow/genesis.json', 'w') as f:
        json.dump(pow_genesis, f, indent=2)

    print(f"已生成PoW版本的创世块配置文件 data/pow/genesis.json")

    # 创建PoS版本的genesis.json
    pos_genesis = create_genesis(accounts, is_pos=True)
    with open('data/pos/genesis.json', 'w') as f:
        json.dump(pos_genesis, f, indent=2)

    print(f"已生成PoS版本的创世块配置文件 data/pos/genesis.json")

if __name__ == "__main__":
    main()
