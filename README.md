# bsv transaction bsv-sdk

![bsv dragon](/docs/SV_dragon_cmyk.gif)
***
Python script to create BSV transactions, check utxos and broadcast BSV to a wallet. Supports Testnet and Mainnet.

Used [BSV Blockchain.org Python Guide](https://docs.bsvblockchain.org/guides/sdks/py)


### Setup
***

Python3 3.9.6 You can install the [bsv-sdk](https://docs.bsvblockchain.org/guides/sdks/py) library or use the requirements.txt file provided.

```
pip install -r requirements.txt
```
or 

```
python3 -m pip install bsv-sdk

python3 -m pip install yenpoint_1satordinals
```

Add your private key locally using the export command. 

```
export PRIVATE_KEY="paste your private key here"
```

Add the wallet address you are sending BSV to by using the export command. 

```
export TARGET_ADDRESS="paste wallet address here" 
```

Send your money

```
python txid_utxo.py
```

To look at your unspent transactions, use the utxos.py script.

My transaction on WhatsonChain using the txid_utxo.py script. [example](https://whatsonchain.com/tx/3ded06b71a4ff8cfdb44f37a2fec9b77d6bae2cf6507ad0d4985e0544e3d965e)

My unspent transactions, the utxos. [example](https://api.whatsonchain.com/v1/bsv/main/address/1PXxMeP14C1A73y8Lf8DNT2o5EWGftGDUV/unspent)


![utxos example](/docs/utxos_example.jpg)


***
`op_return_test.py` is to add a message in the op_return

`1sat_ordinal.py` is to inscribe an image on chain.

***

***
Other: 
non-asyinc.py is a work in progress to not use async. 
 
***


[![In action](https://img.youtube.com/vi/6G97nsB4xqU/maxresdefault.jpg)](https://youtu.be/6G97nsB4xqU)


***
![BSV Dragon](https://github.com/rachyrachyrach/bsv-transaction-bsv-sdk/blob/main/docs/dragon_rainbow_bsv_coin.JPG)
