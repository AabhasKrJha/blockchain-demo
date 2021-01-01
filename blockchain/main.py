# imports ________________________________________________________________________

from flask import Flask, redirect, render_template
import hashlib
import json
import time
import os
import shutil


# app declaration and app configs________________________________________________


app = Flask(__name__)
app.debug = True


# blockchain functions _________________________________________________________________


try:
    os.mkdir('nodes')
except:
    pass


def get_nodes_dir():
    cwd = os.getcwd()
    nodes_dir = os.path.join(cwd, 'nodes')
    return nodes_dir


def calc_hash(data):
    if str(type(data)) == "<class 'dict'>":
        DATA = json.dumps(data)
    else:
        DATA = data
    hash = hashlib.sha256(DATA.encode()).hexdigest()
    return hash


blockchain = []
genesis_block = {
    'index': 0,
    'prev_hash': calc_hash('The_Genesis_Block_Hash'),
    'timestamp': 0,
    'transation': '[none]',
    'proof': 0
}


nodes_dir = get_nodes_dir()
if len(os.listdir(nodes_dir)) != 0:
    node = os.path.join(nodes_dir, 'node0.json')
    with open(node, 'r') as f:
        try:
            data = json.load(f)
            blockchain = data
        except:
            blockchain = [genesis_block]
else:
    blockchain = [genesis_block]


def verify_nodes():
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    nodes_data = []
    if len(nodes) != 0:
        for node in nodes:
            node_name = os.path.join(nodes_dir, node)
            try:
                with open(node_name) as NODE:
                    node_data = json.load(NODE)
                    nodes_data.append(node_data)
            except:
                return True
        response = True
        last_index = len(nodes_data) - 1
        try:
            while response == True:
                if nodes_data[last_index] == nodes_data[last_index-1]:
                    response = True
                    last_index -= 1
                    if last_index == 0:
                        return True
                else:
                    return False
        except:
            return True
    else:
        return True


def distibute_chain():
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    for node in nodes:
        node_name = os.path.join(nodes_dir, node)
        with open(node_name, 'w') as f:
            json.dump(blockchain, f, indent=4)


def add_node():
    nodes_verified = verify_nodes()
    if nodes_verified:
        nodes_dir = get_nodes_dir()
        nodes = os.listdir(nodes_dir)
        node_name = os.path.join(nodes_dir, f'node{len(nodes)}.json')
        with open(node_name, 'w') as node:
            json.dump(blockchain, node, indent=4)
        distibute_chain()


def verify_chain():
    chain_len = len(blockchain)
    if chain_len == 1:
        if blockchain[0] == genesis_block:
            return True
    else:
        last_index = chain_len - 1
        response = True
        while response == True:
            if blockchain[last_index]['prev_hash'] == calc_hash(blockchain[last_index - 1]):
                response = True
                last_index -= 1
                if last_index == 0:
                    if blockchain[last_index] == genesis_block:
                        return True
                    else:
                        return False
            else:
                return False


def add_block():
    chain_verified = verify_chain()
    nodes_verified = verify_nodes()
    if chain_verified and nodes_verified:
        prev_block = blockchain[len(blockchain) - 1]
        block = {
            'index': len(blockchain),
            'prev_hash': calc_hash(json.dumps(prev_block)),
            'timestamp': time.time(),
            'transaction': '[sender, amt, reciever]',
            'proof': bin(len(blockchain))[2:]
        }
        blockchain.append(block)
        distibute_chain()


def clear_network():
    blockchain.clear()
    nodes_dir = get_nodes_dir()
    shutil.rmtree(nodes_dir)
    os.mkdir('nodes')
    blockchain.append(genesis_block)
    add_node()


# app routes__________________________________________________________________


@app.route('/')
def main():
    return redirect('/chain')


@app.route('/chain')
def show_chain():
    chain_length = len(blockchain) - 1
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    node_count = len(nodes)
    if node_count == 0:
        return redirect('/clear')
    return render_template('main.htm', chain_length=chain_length, node_count=node_count, chain=blockchain)


@app.route('/mine')
def mine():
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    if len(nodes) == 0:
        return redirect('/clear')
    initial_chain_len = len(blockchain)
    add_block()
    final_chain_len = len(blockchain)
    if final_chain_len - initial_chain_len == 0:
        return redirect('/clear')
    return redirect('/chain')


@app.route('/block/<int:index>')
def get_index_block(index):
    nodes_dir = get_nodes_dir()
    if len(os.listdir(nodes_dir)) == 0:
        return redirect('/clear')
    chain_len = len(blockchain) - 1
    if index < 0:
        return f'index {index} not found in the blockchain'
    elif index <= chain_len:
        block = json.dumps(blockchain[index])
        return block
    else:
        return 'Block Not Found'


@app.route('/add-node')
def new_node():
    add_node()
    return redirect('/chain')


@app.route('/node/<int:node>')
def view_node(node):
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    node_name = f'node{node}.json'
    if node_name in nodes:
        chain = blockchain
        node_count = f'this is {node_name[:5]}'
        chain_length = len(blockchain)
        return render_template('main.htm', chain=chain, node_count=node_count, chain_length=chain_length)
    else:
        msg = f'{node_name} not found'
        return msg


@app.route('/clear')
def clear_chain():
    clear_network()
    return redirect('/chain')


# running the app_____________________________________________________________


if __name__ == "__main__":
    nodes_dir = get_nodes_dir()
    nodes = os.listdir(nodes_dir)
    if len(nodes) == 0:
        add_node()
    app.run()
