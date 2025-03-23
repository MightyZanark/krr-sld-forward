from model import Symbol, Or, And, Not, Implies
from typing import List, Union
from parser import parse

def forward_chaining(knowledge_base: List[Union[Symbol, Implies, And, Or, Not]]) -> List[Symbol]:
    inferred = set()
    new_facts = True

    while new_facts:
        new_facts = False
        for rule in knowledge_base:
            if isinstance(rule, Implies):
                premise = rule.premise
                conclusion = rule.conclusion
                if premise in inferred and conclusion not in inferred:
                    inferred.add(conclusion)
                    new_facts = True
            elif isinstance(rule, And):
                if rule.op1 in inferred and rule.op2 in inferred:
                    inferred.add(rule)
                    new_facts = True
            elif isinstance(rule, Symbol):
                if rule not in inferred:
                    inferred.add(rule)
                    new_facts = True

    return list(inferred)

def is_solved(solved: List[Union[Symbol, Implies, And, Or, Not]], query: Union[Symbol, Or, Not]) -> bool:
    if isinstance(query, Symbol):
        return query in solved

    if isinstance(query, Not):
        return query.symbol in solved

    return is_solved(solved, query.op1) and is_solved(solved, query.op2)

def sld_resolution(knowledge_base: List[Union[Symbol, Implies, And, Or, Not]], goals: List[Symbol]) -> str:
    solved = []

    while True:
        # Step 1: If all goals are solved, return YES
        if all(goal in solved for goal in goals):
            return "YES"

        # Step 2: Find a clause [p, -p1, ..., -pn] where all -pi are solved and p is not solved
        found_clause = False
        for clause in knowledge_base:
            if isinstance(clause, Implies):
                # Convert implication to CNF: A → B ≡ ¬A ∨ B
                premise = clause.premise
                conclusion = clause.conclusion
                if isinstance(premise, Symbol) and premise in solved and conclusion not in solved:
                    solved.append(conclusion)
                    found_clause = True
                    break
            elif isinstance(clause, And):
                # Handle AND clauses (if needed)
                pass
            elif isinstance(clause, Or):
                # Handle OR clauses (if needed)
                found_solved = False
                pos = None
                for op in clause.operands:
                    if not isinstance(op, Not):
                        if op not in solved:
                            found_solved = True
                            pos = op
                    else:
                        if op.expr not in solved:
                            found_solved = False
                            break

                if found_solved and pos is not None:
                    solved.append(pos)
                    found_clause = True
                    break
                else:
                    continue

            elif isinstance(clause, Symbol):
                # Handle atomic symbols
                if clause not in solved:
                    solved.append(clause)
                    found_clause = True
                    break

        # Step 4: If no such clause is found, return NO
        if not found_clause:
            return "NO"

if __name__ == "__main__":
    knowledge_base = list(parse("tc1.cnf")[0])

    goals = [Symbol("4"), Symbol("3")]

    for i, rule in enumerate(knowledge_base):
        if isinstance(rule, Implies):
            knowledge_base[i] = rule.to_cnf()

    # Perform SLD resolution
    result = sld_resolution(knowledge_base, goals)
    print("Result:", result)  # Output: "YES" or "NO"
