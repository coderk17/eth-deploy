'''
此文件用于启动以太坊Geth客户端。

主要功能:
1. 根据指定的模式（PoW或PoS）启动相应的Geth节点
2. 使用Docker容器运行Geth客户端
3. 配置网络参数、挖矿设置和HTTP API

使用方法:
1. 确保Docker已安装并运行
2. 准备好相应模式的数据目录和创世区块配置文件
3. 调用geth_start()函数，指定PoW或PoS模式和数据目录路径
   例如：geth_start('pow', 'data')
        或 geth_start('pos', 'data')
'''
import json
import time
import os
import subprocess
import sys

def geth_start(mode, accounts_file, data_dir):
    with open(accounts_file, 'r') as f:
        accounts = json.load(f)
    account = accounts[0]

    # 根据模式选择适当的数据目录和Docker镜像
    if mode == 'pow':
        ethereum_dir = os.path.join(data_dir, 'pow')
        docker_image = 'geth:pow'
    elif mode == 'pos':
        ethereum_dir = os.path.join(data_dir, 'pos')
        docker_image = 'geth:pos'
    else:
        raise ValueError("Invalid mode. Use 'pow' or 'pos'.")

    # 检查容器是否存在
    check_container_command = ['docker', 'ps', '-aq', '-f', f'name=geth-{mode}']
    container_id = subprocess.run(check_container_command, capture_output=True, text=True).stdout.strip()

    if container_id:
        # 如果容器已存在,先停止并删除它
        stop_container_command = ['docker', 'stop', container_id]
        remove_container_command = ['docker', 'rm', container_id]
        subprocess.run(stop_container_command, check=True)
        subprocess.run(remove_container_command, check=True)
        print(f"已停止并删除现有的 {mode} 容器")

    # 创建并启动新容器
    create_container_command = [
        'docker', 'run', '-d', '--name', f'geth-{mode}', '--rm',
        '-v', f'{os.path.abspath(ethereum_dir)}:/root/.ethereum',
        '-v', f'{os.path.join(os.path.abspath(ethereum_dir), "genesis.json")}:/root/genesis.json',
        docker_image,
        'init', '/root/genesis.json'
    ]
    result = subprocess.run(create_container_command, check=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"成功创建 {mode} 容器")

    time.sleep(1)

    # 启动节点
    if mode == 'pow':
        start_node_command = [
            'docker', 'run', '-d',
            '--name', f'geth-{mode}',
            '-v', f'{os.path.abspath(ethereum_dir)}:/root/.ethereum',
            '-p', '8545:8545',
            docker_image,
            '--datadir', '/root/.ethereum',
            '--networkid', '193284561987324', 
            '--mine',
            '--miner.threads=1',
            '--miner.etherbase', f'{account["address"]}',
            '--http', '--http.addr', '0.0.0.0',
            '--http.port', '8545',
            '--http.api', 'eth,net,web3,personal,miner',
            '--ipcdisable'
        ]
    elif mode == 'pos':
        start_node_command = [
            'docker', 'run', '-d',
            '--name', f'geth-{mode}',
            '-v', f'{os.path.abspath(ethereum_dir)}:/root/.ethereum',
            '-p', '8545:8545',
            docker_image,
            '--datadir', '/root/.ethereum',
            '--networkid', '193284561987324',
            '--mine',
            '--http', '--http.addr', '0.0.0.0',
            '--http.port', '8545',
            '--http.api', 'eth,net,web3,personal',
            '--mine',
            '--miner.etherbase', f'{account["address"]}',
            '--ipcdisable',
            '--syncmode', 'full',
            '--gcmode', 'archive',
            '--allow-insecure-unlock',
            '--unlock', f'{account["address"]}',
            '--password', '/dev/null'
        ]
    
    subprocess.run(start_node_command, check=True)

    # 如果是 POS 模式，添加验证者
    if mode == 'pos':
        time.sleep(5)  # 等待节点启动
        add_validator_command = [
            'docker', 'exec', f'geth-{mode}',
            'geth', '--exec', f'clique.propose("{account["address"]}", true)',
            'attach', 'http://localhost:8545'
        ]
        try:
            subprocess.run(add_validator_command, check=True, capture_output=True, text=True)
            print(f"已成功将 {account['address']} 添加为验证者")
        except subprocess.CalledProcessError as e:
            print(f"添加验证者失败: {e.stderr}")

    print(f"已在后台启动 {mode.upper()} 节点")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['pow', 'pos']:
        print("Usage: python geth_start.py <pow|pos>")
        sys.exit(1)

    mode = sys.argv[1]
    accounts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'accounts.json')
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    geth_start(mode, accounts_file, data_dir)
