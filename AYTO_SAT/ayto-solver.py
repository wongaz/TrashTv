from __future__ import division  # safety with double division

from pyomo.core.base.set import IndexedSet
from pyomo.environ import *
from pyomo.opt import SolverFactory

infinity = float('inf')
model = AbstractModel()
model.name = "Oracle Solver"

model.NumOfWeeks = Param(within=NonNegativeIntegers)
model.Week = RangeSet(1, model.NumOfWeeks)

model.Male = Set()
model.Female = Set()
model.TruthBoothFalsePair = IndexedSet(model.Male,model.Female)

model.Beams = Param(model.Week, within=NonNegativeIntegers)
model.Assignment = Param(model.Male, model.Female, model.Week, default=0.0, within=Binary)

model.TruthBoothFalse = Param(model.TruthBoothFalsePair, within=Binary)
# model.TruthBoothTrue = Param(model.Male, model.Female, default=0.0, within=Binary)


model.PerfectMatch = Var(model.Male, model.Female, within=Binary)


def optimality_condition(model):
    return sum(model.PerfectMatch[i, j] \
               for i in model.Male \
               for j in model.Female)


model.optimization = Objective(rule=optimality_condition, sense=maximize)


def only_one_rule(model, boys):
    return sum(model.PerfectMatch[boys, g] for g in model.Female) <= 1


model.limit_one_rule = Constraint(model.Male, rule=only_one_rule)


def derive_match_rule(model, week):
    return sum((model.PerfectMatch[b, g] * model.Assignment[b, g, week] for b in model.Male for g in model.Female)) == \
        model.Beams[week]


model.match_rule = Constraint(model.Week, rule=derive_match_rule)

def truth_booth_false(model, b, g):
    if (b, g) in model.TruthBoothFalsePair:
        return model.TruthBoothFalse[b, g] * model.PerfectMatch[b, g] <= 0
    else:
        return Constraint.Skip()


model.failed_truth_booth = Constraint(model.Male, model.Female, rule=truth_booth_false)

# def truth_booth_true(model, b, g):
#     if (b, g) in model.TruthBoothTrue:
#         return model.TruthBoothTrue[b, g] * model.PerfectMatch[b, g] >= 1
#     else:
#         return Constraint.Skip()
# model.successful_truth_booth = Constraint(model.Male, model.Female, rule=truth_booth_true)

instance = model.create_instance("Season/1/S1_EP4.dat")

# Indicate which solver to use
Opt = SolverFactory("appsi_highs")

# Generate a solution
Soln = Opt.solve(instance)
instance.solutions.load_from(Soln)

# Print the output
print("Termination Condition was " + str(Soln.Solver.Termination_condition))
display(instance)
