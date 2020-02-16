# python-chain
POC of blockchain using python. Based on Haseeb Qureshi's presentation: https://github.com/Haseeb-Qureshi/lets-build-a-blockchain

The front end is an api, developped with flask_restplus to generate a swagger interface

goal is to be able to start several clients on localhost with different ports and have the blockchain broadcasted between the nodes.



how to use:
start 3 nodes/client instances:

py app.py 8888 alice 8888 h

py app.py 8889 bob 8888 h

py app.py 8890 charlie 8888,8889 d

alice and bob are honest nodes/clients
charlie is dishonest

the genesis block generates 1000 tokens for alice

from alice's node, send transaction of 200 tokens from alice to bob -> accepted by all 3 nodes
from charlie's node, send transaction of 100 tokens from charlie to alice -> rejected by alice's and bob's nodes
from bob's node, send transacction of 100 tokens to alice  -> accepted by alice's and bob's nodes

future possible improvements:
 - provide cryptographic transaction signature + verification
 - implement gossip protocol with ability for a node to drop out and resynchronize
