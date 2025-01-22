#!/usr/bin/env python3
# From https://github.com/rachyrachyrach/bsv_bsnake
#from bitsv import Key, PrivateKey

# Small Molly https://bico.media/fa30c0e1384fc78204d259c0957676c403ea73f04777bc54a9dc7e2f3af70d70
# Large Molly https://bico.media/db8063c6c806ec1a2ddcc1005f4b9dbcef110c3c83c3cb28abf87ad0fc46b812

#Example output from https://github.com/unwriter/B
#OP_RETURN
#  19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut
#  [Data]
#  [Media Type]
#  [Encoding]
#  [Filename]

#B Crap example
#OP_RETURN 19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut  <html><body>hello world</body></html>  text/html  UTF-8  hello.html

#Wallet on Testnet. Wallet address: n2Ff2TRZqypeeTyHdajfcfsidVDt1nmC2K
my_key = Key.from_hex('e80e48bc6eb32dc0f323f69a14f82bd1b32cbaed8308284e9d3b58cdb5d9dcf2', network='test')

#Wallet on Mainnet. Wallet address: 12uemtEkNkTpX3yQttd7P8p2fP8Giy2qSe
#Wallet private key Hex: 1965714ec753091ec034bc44e6cb0e6adbe453ee6893a0f8ffb13924705f9377
#my_key = Key.from_hex('1965714ec753091ec034bc44e6cb0e6adbe453ee6893a0f8ffb13924705f9377', network='main')

with open("docs/wordmark_and_logo_spacing.PNG", "rb") as fp:
    wordmark_and_logo_spacing = fp.read()

list_of_pushdata = [
    "19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut".encode('utf-8'),
    wordmark_and_logo_spacing,
    "image/png".encode('utf-8'),
    "binary".encode('utf-8'),
    "wordmark_and_logo_spacing.PNG".encode('utf-8')
]

txid = my_key.send_op_return(list_of_pushdata)

print(txid)