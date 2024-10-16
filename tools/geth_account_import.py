"""
此文件用于将预生成的以太坊账户导入到Geth客户端。

主要功能:
1. 从JSON文件中读取账户信息（地址和私钥）
2. 使用Docker运行Geth客户端，并通过命令行导入每个账户
3. 处理导入过程中的错误，并提供反馈
4. 支持POW和POS两种模式

使用方法:
1. 确保Docker已安装并运行
2. 准备包含账户信息的JSON文件（默认路径：data/accounts.json）
3. 运行此脚本以导入账户，指定POW或POS模式
   例如：python geth_account_import.py pow
        或 python geth_account_import.py pos
"""
import json
import subprocess
import os
import tempfile
import sys

def clean_private_key(private_key):
    # 移除可能的"0x"前缀
    private_key = private_key.strip().replace('0x', '')
    # 确保私钥长度为64个字符
    if len(private_key) != 64:
        raise ValueError(f"Invalid private key length: {len(private_key)}")
    return private_key

def check_and_pull_image(mode):
    # 检查镜像是否存在
    check_image_command = ['docker', 'images', '-q', f'geth:{mode}']
    image_exists = subprocess.run(check_image_command, capture_output=True, text=True).stdout.strip()
    
    if not image_exists:
        print(f"geth:{mode} 镜像不存在，正在拉取并打标签...")
        # 根据模式拉取特定版本的以太坊客户端镜像
        if mode == 'pow':
            pull_command = ['docker', 'pull', 'ethereum/client-go:v1.10.26']
        elif mode == 'pos':
            pull_command = ['docker', 'pull', 'ethereum/client-go:v1.13.8']
        else:
            raise ValueError("无效的模式。请使用 'pow' 或 'pos'。")
        subprocess.run(pull_command, check=True)
        
        # 为拉取的镜像打标签
        if mode == 'pow':
            tag_command = ['docker', 'tag', 'ethereum/client-go:v1.10.26', f'geth:{mode}']
        elif mode == 'pos':
            tag_command = ['docker', 'tag', 'ethereum/client-go:v1.13.8', f'geth:{mode}']
        subprocess.run(tag_command, check=True)
        
        print(f"已成功拉取并标记 geth:{mode} 镜像")
    else:
        print(f"geth:{mode} 镜像已存在")

def import_accounts(accounts_file, data_dir, mode):
    # 从JSON文件中读取账户信息
    with open(accounts_file, 'r') as f:
        accounts = json.load(f)

    # 遍历每个账户并导入私钥
    for account in accounts:
        try:
            private_key = clean_private_key(account['private_key'])
        except ValueError as e:
            print(f"跳过无效的私钥 (地址: {account['address']}): {str(e)}")
            continue
        
        # 创建临时文件来存储私钥
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(private_key)
            temp_file_path = temp_file.name

        try:
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
            
            # 如果容器存在，则删除
            if container_id:
                remove_container_command = ['docker', 'rm', '-f', f'geth-{mode}']
                subprocess.run(remove_container_command, check=True)
                print(f"已删除现有的 geth-{mode} 容器")

            # 使用docker run执行导入命令
            import_command = [
                'docker', 'run', '--rm',
                '-v', f'{os.path.abspath(ethereum_dir)}:/root/.ethereum',
                '-v', f'{temp_file_path}:/tmp/keyfile',
                docker_image,
                'account', 'import', '--datadir', '/root/.ethereum',
                '--password', '/dev/null',
                '/tmp/keyfile'
            ]

            # 使用subprocess执行Docker命令
            process = subprocess.run(
                import_command,
                capture_output=True,
                text=True
            )

            # 检查导入结果并打印相应信息
            if process.returncode == 0:
                print(f"成功导入账户 ({mode.upper()}): {account['address']}")
            else:
                print(f"导入账户失败 ({mode.upper()}): {account['address']}")
                print(f"错误信息: {process.stderr}")

        except subprocess.CalledProcessError as e:
            print(f"导入账户失败 ({mode.upper()}): {account['address']}")
            print(f"错误信息: {e.stderr}")
        except Exception as e:
            print(f"导入账户时发生未知错误 ({mode.upper()}): {account['address']}")
            print(f"错误信息: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['pow', 'pos']:
        print("Usage: python geth_account_import.py <pow|pos>")
        sys.exit(1)

    mode = sys.argv[1]
    accounts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'accounts.json')
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # 在导入账户之前检查并拉取镜像
    check_and_pull_image(mode)
    import_accounts(accounts_file, data_dir, mode)
