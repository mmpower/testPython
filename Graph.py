class MyQueue:
	def __init__(self):
		self.items = []
	
	def isEmpty(self):
		return self.items == []
	
	def enqueue(self, item):
		self.items.insert(0,item);
	
	def dequeue(self):
		return self.items.pop();
	

class GraphNode:
	
	def __init__(self, value):
		self.neighbors=[];
		self.value = value;
		self.visited = False;
		
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return str(self.value)	
		
	def addNeighbor(self, node):
		self.neighbors.append(node);
	
	def visit(self):
		print "node %s visited" %( self.value);
		self.visited = True;	
		
		
	def traverseBSF(self):
		self.visit()
		
		queue1 = MyQueue();
		queue1.enqueue(self);
		
		while not queue1.isEmpty():
			print queue1.items;
			
			node = queue1.dequeue();
			#node.visited = true;
			
			for node1 in node.neighbors:
				if not node1.visited: #needed for graph; not needed for trees
					node1.visit();
					queue1.enqueue(node1);
				
def createGraph(parent, depth, maxDepth):
	if depth >= maxDepth:
		return;
	
	for  i in [parent.value+1, parent.value +3]:
		node= GraphNode(i);
		parent.addNeighbor(node)
		createGraph(node,depth+1, maxDepth)
			
		
def testTraverse():
	parent = GraphNode(0);
	createGraph(parent, 0, 4)
	parent.traverseBSF()
			
if __name__ == "__main__":
	testTraverse()
	
						
	
		
		
