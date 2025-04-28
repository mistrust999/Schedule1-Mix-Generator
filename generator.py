import argparse
import random
import sys
from collections import deque
from datetime import datetime
import textwrap
from math import floor

BASE_DRUGS = {
    "OG Kush":           {"base_effects": set(),         "craft_cost": 30,  "yield_units": 10, "base_price": 38},
    "Sour Diesel":       {"base_effects": set(),         "craft_cost": 35,  "yield_units": 10, "base_price": 40},
    "Green Crack":       {"base_effects": set(),         "craft_cost": 40,  "yield_units": 10, "base_price": 43},
    "Granddaddy Purple": {"base_effects": {"Sedating"},  "craft_cost": 45,  "yield_units": 10, "base_price": 44},
    "Meth":              {"base_effects": set(),         "craft_cost": 140, "yield_units": 10, "base_price": 70},
    "Cocaine":           {"base_effects": set(),         "craft_cost": 245, "yield_units": 10, "base_price": 150},
}

INGREDIENTS = {
    "Banana":       {"cost": 8,  "add": "Gingeritis",      "replace": {
        "Calming":"Sneaky","Cyclopean":"Thought-Provoking","Disorienting":"Focused",
        "Energizing":"Thought-Provoking","Focused":"Seizure-Inducing",
        "Long-Faced":"Refreshing","Paranoia":"Jennerising",
        "Smelly":"Anti-Gravity","Toxic":"Smelly"
    }},
    "Cuke":         {"cost": 2,  "add": "Energizing",      "replace": {
        "Euphoric":"Laxative","Foggy":"Cyclopean","Gingeritis":"Thought-Provoking",
        "Munchies":"Athletic","Slippery":"Munchies","Sneaky":"Paranoia","Toxic":"Euphoric"
    }},
    "Donut":        {"cost": 3,  "add": "Calorie-Dense",   "replace": {
        "Anti-Gravity":"Slippery","Balding":"Sneaky","Calorie-Dense":"Explosive",
        "Focused":"Euphoric","Jennerising":"Gingeritis","Munchies":"Calming",
        "Shrinking":"Energizing"
    }},
    "Battery":      {"cost": 2,  "add": "Bright-Eyed",     "replace": {
        "Cyclopean":"Glowing","Electrifying":"Euphoric",
        "Munchies":"Calorie-Dense","Tropic Thunder":"Shrinking"
    }},
    "Paracetamol":  {"cost": 3,  "add": "Sneaky",          "replace": {
        "Calming":"Slippery","Electrifying":"Athletic","Energizing":"Paranoia",
        "Focused":"Gingeritis","Glowing":"Toxic","Munchies":"Anti-Gravity",
        "Paranoia":"Balding","Spicy":"Bright-Eyed","Toxic":"Tropic Thunder"
    }},
    "Gasoline":     {"cost": 5,  "add": "Toxic",           "replace": {
        "Sedating":"Munchies","Disorienting":"Glowing","Electrifying":"Disorienting",
        "Energizing":"Spicy","Euphoric":"Energizing","Gingeritis":"Smelly",
        "Jennerising":"Sneaky","Laxative":"Foggy","Munchies":"Sedating",
        "Paranoia":"Calming","Shrinking":"Focused","Sneaky":"Tropic Thunder"
    }},
    "Mouth Wash":   {"cost": 4,  "add": "Balding",         "replace": {
        "Calming":"Anti-Gravity","Calorie-Dense":"Sneaky",
        "Explosive":"Sedating","Focused":"Jennerising"
    }},
    "Energy Drink": {"cost": 6,  "add": "Athletic",        "replace": {
        "Balding":"Schizophrenic","Foggy":"Laxative","Electrifying":"Euphoric",
        "Energizing":"Focused","Shrinking":"Foggy","Glowing":"Disorienting",
        "Schizophrenic":"Balding","Sedating":"Munchies","Munchies":"Spicy",
        "Spicy":"Euphoric","Tropic Thunder":"Sneaky"
    }},
    "Mega Bean":    {"cost": 7,  "add": "Foggy",           "replace": {
        "Athletic":"Laxative","Calming":"Glowing","Energizing":"Cyclopean",
        "Focused":"Disorienting","Jennerising":"Paranoia","Seizure-Inducing":"Focused",
        "Shrinking":"Electrifying","Slippery":"Shrinking","Sneaky":"Calming",
        "Thought-Provoking":"Cyclopean"
    }},
    "Motor Oil":    {"cost": 6,  "add": "Slippery",        "replace": {
        "Energizing":"Munchies","Euphoric":"Sedating","Foggy":"Toxic",
        "Munchies":"Schizophrenic","Paranoia":"Anti-Gravity"
    }},
    "Iodine":       {"cost": 8,  "add": "Jennerising",     "replace": {
        "Calming":"Balding","Calorie-Dense":"Gingeritis","Euphoric":"Seizure-Inducing",
        "Foggy":"Paranoia","Refreshing":"Thought-Provoking","Toxic":"Sneaky"
    }},
    "Horse Semen":  {"cost": 9,  "add": "Long-Faced",      "replace": {
        "Anti-Gravity":"Tropic Thunder","Athletic":"Euphoric",
        "Laxative":"Refreshing","Gingeritis":"Thought-Provoking","Electrifying":"Glowing"
    }},
    "Chili":        {"cost": 7,  "add": "Spicy",           "replace": {
        "Anti-Gravity":"Tropic Thunder","Athletic":"Euphoric",
        "Laxative":"Long-Faced","Munchies":"Toxic","Shrinking":"Refreshing",
        "Sneaky":"Bright-Eyed"
    }},
    "Flu Medicine": {"cost": 5,  "add": "Sedating",        "replace": {
        "Euphoric":"Laxative","Focused":"Calming","Refreshing":"Euphoric",
        "Munchies":"Slippery","Shrinking":"Slippery","Paranoia":"Thought-Provoking",
        "Thought-Provoking":"Gingeritis"
    }},
    "Addy":         {"cost": 9,  "add": "Thought-Provoking","replace": {
        "Explosive":"Euphoric","Foggy":"Energizing","Glowing":"Refreshing",
        "Long-Faced":"Electrifying","Sedating":"Gingeritis"
    }},
    "Viagra":       {"cost": 4,  "add": "Tropic Thunder",  "replace": {
        "Disorienting":"Toxic","Euphoric":"Bright-Eyed","Laxative":"Calming"
    }},
}

EFFECT_MULTIPLIERS = {
    "Anti-Gravity":      0.54, "Athletic":     0.32, "Balding":      0.30,
    "Bright-Eyed":       0.40, "Calming":      0.10, "Calorie-Dense":0.28,
    "Cyclopean":         0.56, "Disorienting": 0.00, "Electrifying":0.50,
    "Energizing":        0.22, "Euphoric":     0.18, "Explosive":    0.00,
    "Focused":           0.16, "Foggy":        0.36, "Gingeritis":   0.20,
    "Glowing":           0.48, "Jennerising":  0.42, "Laxative":     0.00,
    "Lethal":            0.00, "Long-Faced":   0.52, "Munchies":     0.12,
    "Paranoia":          0.00, "Refreshing":   0.14, "Schizophrenic":0.00,
    "Sedating":          0.26, "Seizure-Inducing":0.00,"Shrinking":  0.60,
    "Slippery":          0.34, "Smelly":       0.00, "Sneaky":       0.24,
    "Spicy":             0.38, "Thought-Provoking":0.44,"Toxic":    0.00,
    "Tropic Thunder":    0.46, "Zombifying":   0.58,
}

ALL_EFFECTS = list(EFFECT_MULTIPLIERS)
MAX_EFFECTS = 8

DRUG_MAP       = {d.lower(): d for d in BASE_DRUGS}
EFFECT_MAP     = {e.lower(): e for e in ALL_EFFECTS}
INGREDIENT_MAP = {i.lower(): i for i in INGREDIENTS}

def validate_drug(x):
    key = x.lower()
    if key not in DRUG_MAP:
        raise ValueError(f"Invalid drug: {x}")
    return DRUG_MAP[key]

def validate_ingredient(x):
    key = x.lower()
    if key not in INGREDIENT_MAP:
        raise ValueError(f"Invalid ingredient: {x}")
    return INGREDIENT_MAP[key]

def apply_ingredient(effects, ing):
    rules = INGREDIENTS[ing]
    new = set(effects)

    for old, new_eff in rules["replace"].items():
        if old in new:
            new.remove(old)
            new.add(new_eff)

    if rules["add"]:
        new.add(rules["add"])
    return frozenset(new)

def find_recipe(base_eff, target_eff, debug=False):
    start = frozenset(base_eff)
    q = deque([(start, [])])
    seen = {start}
    while q:
        effs, steps = q.popleft()
        for ing in INGREDIENTS:
            new_e = apply_ingredient(effs, ing)
            if len(new_e) > MAX_EFFECTS:
                continue
            path = steps + [ing]
            if debug:
                print(f"[DEBUG] {' -> '.join(path)} -> {new_e}")
            if target_eff.issubset(new_e):
                return path
            if new_e not in seen:
                seen.add(new_e)
                q.append((new_e, path))
    return None

def calculate_price_and_profit(drug, recipe):
    base = BASE_DRUGS[drug]
    cost = base["craft_cost"] + sum(INGREDIENTS[i]["cost"] for i in recipe)
    effs = set(base["base_effects"])
    for i in recipe:
        effs = set(apply_ingredient(effs, i))
    mult = sum(EFFECT_MULTIPLIERS.get(e, 0) for e in effs)
    unit = floor(base["base_price"] * (1 + mult))
    rev  = floor(unit * base["yield_units"])
    prof = rev - cost
    return cost, rev, prof, effs, unit

def interactive_find():
    d = None
    while d is None:
        try:
            d = validate_drug(input("Base drug: ").strip())
        except ValueError as e:
            print(e)
    effs = []
    while not effs:
        raw = input("Desired effects (comma-separated): ").split(",")
        try:
            effs = [EFFECT_MAP[e.strip().lower()] for e in raw if e.strip()]
        except KeyError as ke:
            print(f"Invalid effect: {ke}. Try again.")
            effs = []
    print()
    recipe = find_recipe(BASE_DRUGS[d]["base_effects"], set(effs))
    if not recipe:
        print("No recipe found under 8-effect cap.")
        return
    cost, rev, prof, final, unit = calculate_price_and_profit(d, recipe)
    print(f"Mix: {' -> '.join(recipe)}")
    print(f"Final Effects: {', '.join(final)}")
    print(f"Unit Price: ${unit}, Profit: ${prof}\n")

def interactive_eval():
    d = None
    while d is None:
        try:
            d = validate_drug(input("Base drug: ").strip())
        except ValueError as e:
            print(e)
    ings = []
    while not ings:
        raw = input("Ingredients (comma-separated): ").split(",")
        try:
            ings = [validate_ingredient(i.strip()) for i in raw if i.strip()]
        except ValueError as e:
            print(e)
            ings = []
    cost, rev, prof, final, unit = calculate_price_and_profit(d, ings)
    print(f"\nMix: {' -> '.join(ings)}")
    print(f"Final Effects: {', '.join(final)}")
    print(f"Unit Price: ${unit}, Profit: ${prof}\n")

def random_mix():
    d = random.choice(list(BASE_DRUGS))
    k = random.randint(2, 6)
    ings = random.sample(list(INGREDIENTS), k)
    print(f"\nRandom Mix for {d}:")
    print(f"Ingredients: {', '.join(ings)}")
    cost, rev, prof, final, unit = calculate_price_and_profit(d, ings)
    print(f"Mix: {' -> '.join(ings)}")
    print(f"Final Effects: {', '.join(final)}")
    print(f"Unit Price: ${unit}, Profit: ${prof}\n")

def run_menu():
    while True:
        print(textwrap.dedent("""
            Schedule I Mix Generator
            [1] Find recipe by effects
            [2] Evaluate custom mix
            [3] Generate random mix
            [4] Exit
        """))
        choice = input("Choose an option: ").strip()
        if choice == "1":
            interactive_find()
        elif choice == "2":
            interactive_eval()
        elif choice == "3":
            random_mix()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid selection, try 1–4.\n")

def run_args():
    parser = argparse.ArgumentParser(description="Find or evaluate mixes for Schedule I")
    parser.add_argument("--drug", "-d",    type=validate_drug, help="Base drug")
    parser.add_argument("--effects","-e",  nargs="+",         help="Desired effects")
    parser.add_argument("--ingredients","-i",nargs="+",       help="Custom ingredients")
    parser.add_argument("--debug",          action="store_true", help="Debug BFS")
    args = parser.parse_args()

    if not args.drug:
        parser.error("`--drug` is required in argument mode.")
    if not args.effects and not args.ingredients:
        parser.error("Must specify at least one of --effects or --ingredients")

    if args.effects:
        target = set(EFFECT_MAP[e.lower()] for e in args.effects)
        recipe = find_recipe(BASE_DRUGS[args.drug]["base_effects"], target, debug=args.debug)
        if not recipe:
            print("No recipe found.\n")
        else:
            cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, recipe)
            print(f"Mix: {' -> '.join(recipe)}")
            print(f"Effects: {', '.join(final)}")
            print(f"Unit Price: ${unit}, Profit: ${prof}\n")

    if args.ingredients:
        ings = [validate_ingredient(i) for i in args.ingredients]
        cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, ings)
        print(f"Mix: {' -> '.join(ings)}")
        print(f"Effects: {', '.join(final)}")
        print(f"Unit Price: ${unit}, Profit (10x ): ${prof}\n")

if __name__ == "__main__":

    if len(sys.argv) > 1:
        run_args()
    else:
        run_menu()
