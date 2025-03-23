from model import Symbol, Or, And, Not, Implies
from typing import List, Union
from parser import parse
import time
import psutil
import os

def sld_forward_chaining(knowledge_base: List[Union[Symbol, Implies, And, Or, Not]], goals: List[Symbol]) -> str:
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

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 ** 2)

if __name__ == "__main__":
    start_time = time.time()
    print(f"Initial memory usage: {get_memory_usage():.2f} MB\n")

    knowledge_base = list(parse("tc3.cnf")[0])
    for i, rule in enumerate(knowledge_base):
        if isinstance(rule, Implies):
            knowledge_base[i] = rule.to_cnf()

    goals = [Symbol("16"), Symbol("39"), Symbol("51"), Symbol("77")]
    print("Goals:",goals)

    # Perform SLD resolution
    result = sld_forward_chaining(knowledge_base, goals)
    print("Result:", result)
    
    print()
    print(f"Time taken: {time.time() - start_time:.4f} seconds")
    print(f"Final memory usage: {get_memory_usage():.2f} MB")
