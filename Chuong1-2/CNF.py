import re

class Node:
    def __init__(self, op, left=None, right=None):
        self.op = op        # VAR, ¬, ∧, ∨, →, ↔
        self.left = left
        self.right = right

    def __str__(self):
        if self.op == "VAR":
            return self.left
        if self.op == "¬":
            return f"¬{self.left}"
        return f"({self.left} {self.op} {self.right})"

def tokenize(expr):
    expr = expr.replace(" ", "")
    # Thứ tự quan trọng
    tokens = re.findall(r'↔|→|[A-Z]|[()¬∧∨]', expr)
    return tokens

def parse(tokens):
    def parse_expr():
        return parse_equiv()

    def parse_equiv():
        node = parse_imp()
        while tokens and tokens[0] == "↔":
            tokens.pop(0)
            node = Node("↔", node, parse_imp())
        return node

    def parse_imp():
        node = parse_or()
        while tokens and tokens[0] == "→":
            tokens.pop(0)
            node = Node("→", node, parse_or())
        return node

    def parse_or():
        node = parse_and()
        while tokens and tokens[0] == "∨":
            tokens.pop(0)
            node = Node("∨", node, parse_and())
        return node

    def parse_and():
        node = parse_not()
        while tokens and tokens[0] == "∧":
            tokens.pop(0)
            node = Node("∧", node, parse_not())
        return node

    def parse_not():
        if tokens[0] == "¬":
            tokens.pop(0)
            return Node("¬", parse_not())
        elif tokens[0] == "(":
            tokens.pop(0)
            node = parse_expr()
            tokens.pop(0)  # )
            return node
        else:
            return Node("VAR", tokens.pop(0))

    return parse_expr()

def eliminate_imp(node):
    if node is None:
        return None

    if node.op == "→":
        A = eliminate_imp(node.left)
        B = eliminate_imp(node.right)
        return Node("∨", Node("¬", A), B)

    if node.op == "↔":
        A = eliminate_imp(node.left)
        B = eliminate_imp(node.right)
        left = Node("∨", Node("¬", A), B)
        right = Node("∨", Node("¬", B), A)
        return Node("∧", left, right)

    if node.op == "¬":
        node.left = eliminate_imp(node.left)
        return node

    if node.op in ["∧", "∨"]:
        node.left = eliminate_imp(node.left)
        node.right = eliminate_imp(node.right)
        return node

    return node

def push_not(node):
    if node.op == "¬":
        c = node.left
        if c.op == "¬":
            return push_not(c.left)
        if c.op == "∧":
            return Node("∨",
                        push_not(Node("¬", c.left)),
                        push_not(Node("¬", c.right)))
        if c.op == "∨":
            return Node("∧",
                        push_not(Node("¬", c.left)),
                        push_not(Node("¬", c.right)))
        return node

    if node.op in ["∧", "∨"]:
        node.left = push_not(node.left)
        node.right = push_not(node.right)

    return node

def distribute(node):
    if node.op == "∨":
        A = node.left
        B = node.right

        if A.op == "∧":
            return Node("∧",
                        distribute(Node("∨", A.left, B)),
                        distribute(Node("∨", A.right, B)))

        if B.op == "∧":
            return Node("∧",
                        distribute(Node("∨", A, B.left)),
                        distribute(Node("∨", A, B.right)))

    if node.op in ["∧", "∨"]:
        node.left = distribute(node.left)
        node.right = distribute(node.right)

    return node

def to_cnf(expr):
    tokens = tokenize(expr)
    tree = parse(tokens)

    print("Công thức ban đầu:      ", tree)

    step1 = eliminate_imp(tree)
    print("Sau khi bỏ →, ↔:        ", step1)

    step2 = push_not(step1)
    print("Sau khi đẩy phủ định:   ", step2)

    cnf = distribute(step2)
    print("Dạng chuẩn hội (CNF):   ", cnf)

    return cnf

if __name__ == "__main__":
    expr = input("Nhập công thức mệnh đề: ")
    to_cnf(expr)
