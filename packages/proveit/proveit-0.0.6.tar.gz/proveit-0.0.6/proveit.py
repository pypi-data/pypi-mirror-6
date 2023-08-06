from hashlib import sha256
import math
from decimal import Decimal
from bitcoinrpc import *
import time
import simplejson as json

class Node():
	def __init__(self, value, hashdigest):
		value = Decimal(str(value))
		self.value = value
		self.hashdigest = hashdigest
	
def NodeCombiner(left, right):
	newvalue = left.value + right.value
	lefthash, righthash = left.hashdigest, right.hashdigest
	hashdigest = sha256(str(newvalue) + lefthash + righthash).hexdigest()
	
	return Node(newvalue, hashdigest)

class HashTree():
	def __init__(self, nodelist):
		self.nodelist = nodelist
		self.roothash = ''
		self.tree = []
		self.GenTree(nodelist)
		self.lookup = {}
		self.GenLookup()
	
	def ReturnTotal(self):
		return self.tree[-1][0].value
	
	def GenTree(self, nodelist):
		self.tree.append(nodelist)
		newnodelist = []
		
		if len(nodelist) % 2:
			nodelist.append(Node(0.0, sha256('0').hexdigest()))
		
		for x in range(int(math.ceil(len(nodelist)/2.0))):
			newnodelist.append(NodeCombiner(nodelist[(x * 2)], nodelist[(x * 2 + 1)]))
		
		if len(newnodelist) > 1:
			return self.GenTree(newnodelist)
		else:
			self.tree.append(newnodelist)
			self.roothash = newnodelist[0].hashdigest
			return self.roothash
	
	def ValidateTree(self, tree=None):
		if tree == None:
			tree = self.tree
		for x in tree:
			print x
	
	def RegenTree(self):
		self.tree = []
		return self.GenTree(self.nodelist)
	
	def GetInfoFromHash(self, hashdigest):
		index = self.lookup[hashdigest]
		info = self.GetNodeInfo(index)
		verifyinfo = self.GetNodePairList(index)
		return info[0], info[1], verifyinfo[0], verifyinfo[1]
	
	def GetNodeInfo(self, index):
		return str(self.tree[0][index].value), self.tree[0][index].hashdigest
	
	def GetNodePairList(self, index, pairlist=[], tree=None):
		if tree == None:
			tree = self.tree
			pairlist = []
		elif len(tree) == 1:
			return self.roothash, pairlist
		pairlist.append((str(tree[0][index + (-1 if index % 2 else 1)].value), tree[0][index + (-1 if index % 2 else 1)].hashdigest, 0 if index % 2 else 1))
		index = index / 2
		return self.GetNodePairList(index, pairlist=pairlist, tree=tree[1:])
		
	def GenLookup(self):
		index = 0
		for x in self.nodelist:
			self.lookup[x.hashdigest] = index
			index += 1
	
def ValidateNode(node, roothash, pairlist):
	for x in pairlist:
		# If this was an even node, put the paired node on the right, otherwise it goes on the left.
		if x[2]:
			node = NodeCombiner(node, Node(x[0], x[1]))
		else:
			node = NodeCombiner(Node(x[0], x[1]), node)
	return node.hashdigest == roothash

class Coin():
	def __init__(self, host, port, user, password, use_https=False):
		self.conn = connect_to_remote(user, password, host=host, port=port, use_https=use_https)

def ValidateBalance(coin, amount, message="Coin Balance Verified for %s" % time.strftime("%a, %d %b %Y %H:%M:%S +0000")):
	if type(amount) is str:
		amount = Decimal(amount)
	vfdamount = Decimal('0')
	msgs = []
	for x in coin.conn.listunspent():
		if vfdamount < amount:
			vfdamount += x.amount
			msgs.append((x.address, coin.conn.proxy.signmessage(x.address, message)))
	return msgs, vfdamount, message
