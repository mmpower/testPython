# -*- coding: utf-8 -*-

from Graph import MyQueue

class BinaryTree:

    def __init__(self, value):
        self.value = value
        self.visited = False
        self.leftChild = None
        self.rightChild = None
        self.parent = None

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def addLeftChild(self, value):
        self.leftChild = BinaryTree(value)
        self.leftChild.parent = self

    def addRightChild(self, value):
        self.rightChild = BinaryTree(value)
        self.rightChild.parent = self

    def visit(self):
        print self.value
        self.visited = True

    def inOrderTraverse(self):
        if self.leftChild:
            self.leftChild.inOrderTraverse()

        self.visit()

        if self.rightChild:
            self.rightChild.inOrderTraverse()

    def preOrderTraverse(self):
        self.visit()

        if self.leftChild:
            self.leftChild.preOrderTraverse()

        if self.rightChild:
            self.rightChild.preOrderTraverse()

    def postOrderTraverse(self):

        if self.leftChild:
            self.leftChild.postOrderTraverse()

        if self.rightChild:
            self.rightChild.postOrderTraverse()

        self.visit()

def inOrderNext(self):
    if self.rightChild:
        node = self.rightChild
        while node.leftChild:
            node = node.leftChild
        print "next: %s" %(node)
        return node
    node = self
    parent1= node.parent
    while parent1 and parent1.rightChild == node:
        node = parent1
        parent1 = parent1.parent

    print "next: %s" %(parent1)
    return parent1

def buildTree():
    queue1 = MyQueue()
    tree = BinaryTree(0)
    queue1.enqueue(tree)

    i = 0
    while not queue1.isEmpty() and i <= 15:
        node = queue1.dequeue()
        i += 1
        node.addLeftChild(i)
        i += 1
        node.addRightChild(i)
        queue1.enqueue(node.leftChild)
        queue1.enqueue(node.rightChild)

    return tree


if __name__ == "__main__":
    tree= buildTree()
    print "pre order"
    tree.preOrderTraverse()

    print "in order"
    tree.inOrderTraverse()

    print "post order"
    tree.postOrderTraverse()

    BinaryTree.visit = inOrderNext

    tree.preOrderTraverse()


