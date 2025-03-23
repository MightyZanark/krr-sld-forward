from model import Symbol, Or, Not

def build_disjunction(op1: Symbol, op2: set[Symbol] | Symbol) -> Or:

    if op2 == set():
        return op1

    if isinstance(op2, set):
        return Or(op1, build_disjunction(op2.pop(), op2))

    return Or(op1, op2)


def parse(file_name: str) -> tuple[set, set]:
    knowledge_base = set()
    all_symbols = set()

    with open(file_name, "r") as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith("c") or line.startswith("p"):
                continue

            symbols = line.strip().split()[:-1]

            symbols = set(
                [
                    Not(Symbol(symbol.removeprefix("-")))
                    if symbol.startswith("-")
                    else Symbol(symbol)
                    for symbol in symbols
                ]
            )

            all_symbols |= symbols
            knowledge_base.add(build_disjunction(symbols.pop(), symbols))

    return knowledge_base, all_symbols
