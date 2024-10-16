# Windows系统搭建以太坊私链

本指南将帮助您在本地搭建一个以太坊私链。我们提供了POW和POS两个版本的搭建方法。按照以下步骤操作,您将能够创建并运行自己的以太坊私有网络。

## 目录

1. [安装Docker](#1-安装docker)
2. [拉取Geth Docker镜像](#2-拉取geth-docker镜像)
3. [创建创世配置文件](#3-创建创世配置文件)
4. [初始化以太坊私链](#4-初始化以太坊私链)
5. [启动以太坊私链节点](#5-启动以太坊私链节点)
6. [创建账户](#6-创建账户)
7. [开始挖矿或验证](#7-开始挖矿或验证)
8. [验证节点是否工作](#8-验证节点是否工作)
9. [POS版本特殊说明](#9-pos版本特殊说明)

## 1. 安装Docker

Docker是运行以太坊节点的推荐方式。如果您还没有安装Docker,请按照以下步骤进行安装:

1. 访问Docker官网: https://www.docker.com/get-started
2. 下载并安装适合您操作系统的Docker版本
3. 安装完成后,打开终端并运行 `docker --version` 确保安装成功

## 2. 拉取Geth Docker镜像

Geth是最流行的以太坊客户端之一。运行以下命令拉取最新的Geth Docker镜像，并打上标签:

pow版本：

```bash
docker pull ethereum/client-go:v1.10.26
docker tag ethereum/client-go:v1.10.26 geth:pow
```

pos版本：

```bash
docker pull ethereum/client-go:latest
docker tag ethereum/client-go:v1.10.26 geth:pos
```

## 3. 创建创世配置文件

我们提供了一个Python脚本来生成创世配置文件。首先,确保您已安装所需的Python依赖:

```bash
pip install -r tools/requirements.txt
```

然后运行账户和创世块生成脚本:

```bash
python tools/gen_genesis.py
```

这个脚本会生成100个账户,并创建POW和POS两个版本的创世块配置文件。

## 4. 初始化以太坊私链

使用创世配置文件初始化您的私链。对于POW版本:

```bash
docker run --name geth-pow --rm -v ${PWD}\data\pow\genesis.json:/root/genesis.json -v ${PWD}\data\pow:/root/.ethereum geth:pow init /root/genesis.json
```

对于POS版本:

```bash
docker run --name geth-pos --rm -v ${PWD}\data\pos\genesis.json:/root/genesis.json -v ${PWD}\data\pos:/root/.ethereum geth:pos init /root/genesis.json
```

## 5. 启动以太坊私链节点

运行以下命令启动您的私链节点。对于POW版本:

```bash
docker run --name geth-pow -it --rm `
  -p 8545:8545 `
  -v ${PWD}\data\pow:/root/.ethereum `
  geth:pow `
  --networkid 6879676 `
  --http `
  --http.addr "127.0.0.1" `
  --http.port 8545 `
  --http.corsdomain "*" `
  --http.api "eth,net,web3,personal,miner"
```

对于POS版本:

```bash
docker run --name geth-pow -it --rm `
  -p 8545:8545 `
  -v ${PWD}\data\pow:/root/.ethereum `
  ethereum/client-go:v1.13.8 `
  --networkid 193284561987324 `
  --http `
  --http.addr "0.0.0.0" `
  --http.port 8545 `
  --http.corsdomain "*" `
  --http.api "eth,net,web3,personal,miner" `
  --mine `
  --miner.etherbase 0x<YOUR_VALIDATOR_ADDRESS>
```

请将 `<YOUR_VALIDATOR_ADDRESS>` 替换为您想用作验证者的账户地址。

## 6. 创建账户

我们提供了一个Python脚本来生成创世配置文件。首先,确保您已安装所需的Python依赖:

```bash
pip install -r tools/requirements.txt
```

然后运行账户和创世块生成脚本:

```bash
python tools/geth_account_import.py
```

## 7. 开始挖矿或验证

对于POW版本,在Geth控制台中启动挖矿:

```bash
docker exec -it <container_id> geth attach /root/.ethereum/geth.ipc
```

在Geth控制台中,运行:

```javascript
miner.start(1)
```

对于POS版本,验证过程在启动节点时就已经开始。

## 8. 验证节点是否工作

在Geth控制台中,您可以运行以下命令来验证节点是否正常工作:

```javascript
eth.blockNumber  // 查看当前区块高度
eth.accounts     // 查看账户列表
eth.getBalance(eth.accounts[0])  // 查看第一个账户的余额
```

## 9. POS版本特殊说明

对于POS版本,您需要确保:

1. 使用 `genesis_pos.json` 初始化私链。
2. 启动节点时指定了验证者地址。
3. 如果需要添加更多验证者,可以使用 `clique.propose()` 方法。

例如,添加新的验证者:

```javascript
clique.propose("0x<NEW_VALIDATOR_ADDRESS>", true)
```

移除验证者:

```javascript
clique.propose("0x<VALIDATOR_ADDRESS>", false)
```

查看当前的验证者列表:

```javascript
clique.getSigners()
```

注意事项:

1. 请确保在运行Python脚本之前已安装所有必要的依赖。
2. 生成的账户信息存储在 `data/accounts.json` 文件中,请妥善保管这些信息。
3. 如果您需要修改创世块配置,可以编辑 `genesis_pow.json` 或 `genesis_pos.json` 文件。但请注意,修改创世块配置后需要重新初始化私链。
4. 本指南假设您在项目根目录下执行所有命令。如果您在不同的目录下,请相应地调整文件路径。

## 导入账户私钥

在初始化和启动节点之后，您可以使用以下命令导入 `data/accounts.json` 中的账户私钥：

对于 POW 版本：

```bash
python tools/geth_account_import.py pow
```

对于 POS 版本：

```bash
python tools/geth_account_import.py pos
```

这个脚本会读取 `data/accounts.json` 文件，并将其中的私钥导入到您的 Geth 节点中。请确保在运行此脚本之前，您已经初始化了私链并启动了节点。

注意: 这个脚本使用空密码导入私钥。在生产环境中，您应该使用更安全的方法来管理密码。
