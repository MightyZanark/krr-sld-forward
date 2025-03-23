from __future__ import annotations
from dataclasses import dataclass
from typing import Union

Expr = Union["Symbol", "And", "Or", "Not", "Implies", "Iff"]

@dataclass(frozen=True)
class Symbol:
    name: str

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(self, other)

    def __invert__(self):
        return Not(self)

    def __rshift__(self, other):
        return Implies(self, other)

    def __lshift__(self, other):
        return Implies(other, self)

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def to_cnf(self):
        return self

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class And:
    operands: tuple[Expr, ...]

    def __init__(self, *args: Expr):
        flat = []
        for a in args:
            if isinstance(a, And):
                flat.extend(a.operands)
            else:
                flat.append(a)
        unique = list(set(flat))
        object.__setattr__(self, "operands", tuple(unique))

    def to_cnf(self):
        return And(*(op.to_cnf() for op in self.operands))

    def __str__(self):
        return "(" + " ∧ ".join(str(op) for op in self.operands) + ")"

    def __eq__(self, other):
        return isinstance(other, And) and set(self.operands) == set(other.operands)


@dataclass(frozen=True)
class Or:
    operands: tuple[Expr, ...]

    def __init__(self, *args: Expr):
        flat = []
        for a in args:
            if isinstance(a, Or):
                flat.extend(a.operands)
            else:
                flat.append(a)
        unique = list(set(flat))
        object.__setattr__(self, "operands", tuple(unique))

    def to_cnf(self):
        ops = [op.to_cnf() for op in self.operands]

        # Distribusi jika perlu
        for i, op in enumerate(ops):
            if isinstance(op, And):
                rest = ops[:i] + ops[i+1:]
                return And(*(Or(a, *rest).to_cnf() for a in op.operands)).to_cnf()
        return Or(*ops)

    def __str__(self):
        return "(" + " ∨ ".join(str(op) for op in self.operands) + ")"

    def __eq__(self, other):
        return isinstance(other, Or) and set(self.operands) == set(other.operands)


@dataclass(frozen=True)
class Not:
    expr: Expr

    def __eq__(self, other):
        return isinstance(other, Not) and self.expr == other.expr

    def to_cnf(self):
        e = self.expr
        if isinstance(e, Symbol):
            return Not(e)

        elif isinstance(e, Not):
            return e.expr.to_cnf()

        elif isinstance(e, And):
            # ¬(A ∧ B ∧ ...) → ¬A ∨ ¬B ∨ ...
            return Or(*(Not(op).to_cnf() for op in e.operands))

        elif isinstance(e, Or):
            # ¬(A ∨ B ∨ ...) → ¬A ∧ ¬B ∧ ...
            return And(*(Not(op).to_cnf() for op in e.operands))

        elif isinstance(e, Implies):
            # ¬(A ⊃ B) → A ∧ ¬B
            return And(e.premise.to_cnf(), Not(e.conclusion).to_cnf())

        elif isinstance(e, Iff):
            # ¬(A ≡ B) → ¬((A ⊃ B) ∧ (B ⊃ A))
            return Not(e.to_cnf()).to_cnf()

        else:
            raise Exception(f"Unknown NOT expression: {e}")

    def __str__(self):
        if isinstance(self.expr, Symbol):
            return f"¬{self.expr}"
        return f"¬({self.expr})"


@dataclass(frozen=True)
class Implies:
    premise: Expr
    conclusion: Expr
    
    def __eq__(self, other):
        return (
            isinstance(other, Implies)
            and self.premise == other.premise
            and self.conclusion == other.conclusion
        )


    def to_cnf(self):
        return Or(Not(self.premise).to_cnf(), self.conclusion.to_cnf())

    def __str__(self):
        return f"({self.premise} ⊃ {self.conclusion})"


@dataclass(frozen=True)
class Iff:
    left: Expr
    right: Expr

    def __eq__(self, other):
        return isinstance(other, Iff) and (
            (self.left == other.left and self.right == other.right)
            or (self.left == other.right and self.right == other.left)
        )

    def to_cnf(self):
        return And(
            Implies(self.left, self.right).to_cnf(),
            Implies(self.right, self.left).to_cnf(),
        )

    def __str__(self):
        return f"({self.left} ≡ {self.right})"

def is_cnf(expr: Expr) -> bool:
    if not isinstance(expr, And):
        return False
    clause_set = set()
    for clause in expr.operands:
        if clause in clause_set:
            return False
        clause_set.add(clause)
        if isinstance(clause, Or):
            seen = set()
            for literal in clause.operands:
                if not is_literal(literal):
                    return False
                if str(literal) in seen:
                    return False
                seen.add(str(literal))
        elif is_literal(clause):
            continue
        else:
            return False
    return True

def is_literal(expr: Expr) -> bool:
    return isinstance(expr, Symbol) or (isinstance(expr, Not) and isinstance(expr.expr, Symbol))

def convert_to_cnf(expr: Expr) -> Expr:
    while not is_cnf(expr):
        expr = expr.to_cnf()
    return expr
