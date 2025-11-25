class TwoThreeNode():
    def __init__(self, key):
        self.key1 = key
        self.key2 = None
        self.left = None
        self.middle = None
        self.right = None
    
    def is_leaf(self):
        # return True when this node has no children
        return self.left is None and self.middle is None and self.right is None
    
    def has_two_keys(self):
        # Return True if node currently stores two keys.
        return self.key2 is not None

    def has_key(self, key):
        # Return True if key exists in this node.
        return (self.key1 == key) or (self.key2 == key)

    def min_key(self):
        # Return smallest key in node.
        return self.key1 if self.key1 is not None else self.key2

    def max_key(self):
        # Return largest key in node.
        return self.key2 if self.key2 is not None else self.key1

    def add_key(self, key):
        # Insert key into this node when it has only one key.
        # Returns True on success, False if key is duplicate or node already full.
        if self.has_key(key):
            return False
        if self.has_two_keys():
            return False
        # place keys in order
        if key < self.key1:
            self.key2 = self.key1
            self.key1 = key
        else:
            self.key2 = key
        return True

    def remove_key(self, key):
        # Remove a key from node.
        # If removing key1 and key2 exists, shift key2 into key1.
        # Returns True if removal happened, False otherwise.
        if not self.has_key(key):
            return False
        if self.key2 is None:
            # removing the only key - result is an empty node (caller must handle)
            if self.key1 == key:
                self.key1 = None
            return True
        # node has two keys
        if key == self.key1:
            self.key1 = self.key2
            self.key2 = None
        else:
            # key == key2
            self.key2 = None
        return True

    def get_child_for(self, key):
        # Choose child to descend for a given key. Returns one of (left, middle, right) or None.
        if not self.has_two_keys():
            # one key: left < key1, middle >= key1
            if key < self.key1:
                return self.left
            return self.middle
        # two keys: left < key1, middle between key1 and key2, right >= key2
        if key < self.key1:
            return self.left
        if key < self.key2:
            return self.middle
        return self.right

    def get_child_index_for(self, key):
        # Return the index (0-based) of the child pointer we would follow for key.
        # For one-key node: 0 -> left, 1 -> middle
        # For two-key node: 0 -> left, 1 -> middle, 2 -> right
        if not self.has_two_keys():
            return 0 if key < self.key1 else 1
        if key < self.key1:
            return 0
        if key < self.key2:
            return 1
        return 2

    def children_list(self):
        # Return list of children in order (length 2 or 3).
        if self.has_two_keys():
            return [self.left, self.middle, self.right]
        return [self.left, self.middle]

    def set_children_from_list(self, lst):
        # Set left/middle/right from list (len 2 or 3).
        if len(lst) == 2:
            self.left, self.middle = lst
            self.right = None
        else:
            self.left, self.middle, self.right = lst

    def insert_into_leaf(self, key):
        # Insert key into this node assuming it is a leaf.
        # - If key already present: return None (no-op).
        # - If node has room: insert and return None.
        # - If node is full (two keys): split leaf and return (promoted_key, left_node, right_node).
        #   left_node and right_node are new leaf nodes.
        if not self.is_leaf():
            raise ValueError("insert_into_leaf called on non-leaf node")
        if self.has_key(key):
            return None
        if not self.has_two_keys():
            self.add_key(key)
            return None
        # Node has two keys -> will split into two nodes and promote middle key
        keys = sorted([self.key1, self.key2, key])
        left = TwoThreeNode(keys[0])
        right = TwoThreeNode(keys[2])
        promoted = keys[1]
        return (promoted, left, right)

    def __repr__(self):
        if self.key2 is not None:
            return f"TwoThreeNode({self.key1!r}, {self.key2!r})"
        return f"TwoThreeNode({self.key1!r})"


class TwoThreeTree:
    # Simple 2-3 Tree with insertion (proper split handling), search, inorder listing,
    # and deletion implemented by rebuilding the tree without the deleted key.
    def __init__(self):
        self.root = None

    def find(self, key):
        # Return True if key in tree, False otherwise.
        node = self.root
        while node is not None:
            if node.has_key(key):
                return True
            if node.is_leaf():
                return False
            node = node.get_child_for(key)
        return False

    # alias
    def search(self, key):
        return self.find(key)

    def _insert_recursive(self, node, key):
        # Attempt to insert key into subtree rooted at node.
        # Returns None if no split propagated up.
        # If child split causes promotion, returns (promoted_key, left_node, right_node).
        if node.is_leaf():
            return node.insert_into_leaf(key)

        # descend into proper child
        idx = node.get_child_index_for(key)
        children = node.children_list()
        target = children[idx]
        if target is None:
            # malformed tree: create new leaf
            target = TwoThreeNode(key)
            children[idx] = target
            node.set_children_from_list(children)
            return None

        res = self._insert_recursive(target, key)
        if res is None:
            return None  # no split below

        # child split returned a promotion
        promoted, left_child, right_child = res

        # integrate promoted into current node
        if not node.has_two_keys():
            # integrate without splitting node: node will have two keys and three children
            # replace the child at idx with left_child and right_child in order
            children = node.children_list()
            # build new children list by inserting left/right in place of the split child
            new_children = children[:idx] + [left_child, right_child] + children[idx+1:]
            # set new key values in order
            keys = sorted([node.key1, promoted])
            node.key1, node.key2 = keys[0], keys[1]
            # assign children: new_children should have length 3
            node.set_children_from_list(new_children)
            return None
        else:
            # node has two keys -> will need to split this internal node
            # prepare combined keys and combined children (4 children)
            children = node.children_list()
            combined_children = children[:idx] + [left_child, right_child] + children[idx+1:]
            combined_keys = sorted([node.key1, node.key2, promoted])
            # left internal node with smallest key
            left_node = TwoThreeNode(combined_keys[0])
            # right internal node with largest key
            right_node = TwoThreeNode(combined_keys[2])
            # assign children: left gets first two, right gets last two
            left_node.set_children_from_list([combined_children[0], combined_children[1]])
            right_node.set_children_from_list([combined_children[2], combined_children[3]])
            # promote middle key up
            return (combined_keys[1], left_node, right_node)

    def insert(self, key):
        # Insert key into the 2-3 tree.
        if self.root is None:
            self.root = TwoThreeNode(key)
            return True
        # if key exists already, do nothing
        if self.find(key):
            return False
        res = self._insert_recursive(self.root, key)
        if res is None:
            return True
        # root was split -> create new root
        promoted, left_node, right_node = res
        new_root = TwoThreeNode(promoted)
        new_root.left = left_node
        new_root.middle = right_node
        self.root = new_root
        return True

    # alias
    def add(self, key):
        return self.insert(key)

    def _inorder(self, node, out):
        if node is None:
            return
        if node.is_leaf():
            # leaf may have 1 or 2 keys
            out.append(node.key1)
            if node.key2 is not None:
                out.append(node.key2)
            return
        # internal node
        if not node.has_two_keys():
            # one key: left, key1, middle
            self._inorder(node.left, out)
            out.append(node.key1)
            self._inorder(node.middle, out)
        else:
            # two keys: left, key1, middle, key2, right
            self._inorder(node.left, out)
            out.append(node.key1)
            self._inorder(node.middle, out)
            out.append(node.key2)
            self._inorder(node.right, out)

    def to_list(self):
        # Return sorted list of keys (inorder traversal).
        out = []
        self._inorder(self.root, out)
        return out

    def delete(self, key):
        # Delete key from tree. For simplicity and correctness, rebuild tree from remaining keys.
        # Returns True if key was present and deleted, False otherwise.
        if not self.find(key):
            return False
        keys = self.to_list()
        # remove the key (first occurrence)
        keys.remove(key)
        # rebuild tree
        self.root = None
        for k in keys:
            self.insert(k)
        return True

    def __repr__(self):
        return f"TwoThreeTree({self.to_list()})"


# Example usage:
if __name__ == "__main__":
    tree = TwoThreeTree()
    for value in [10, 20, 5, 6, 12, 30, 25]:
        tree.insert(value)
    print("Tree contents (inorder):", tree.to_list())
    print("Find 12:", tree.find(12))            
    print("Find 15:", tree.find(15))
    tree.delete(20)
    print("Tree contents after deleting 20 (inorder):", tree.to_list())