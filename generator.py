import argparse
from collections import deque
from datetime import datetime
import textwrap

BASE_DRUGS = {
    "OG Kush":           {"base_effects": set(),         "craft_cost": 30,  "yield_units": 10, "base_price": 38},
    "Sour Diesel":       {"base_effects": set(),         "craft_cost": 35,  "yield_units": 10, "base_price": 40},
    "Green Crack":       {"base_effects": set(),         "craft_cost": 40,  "yield_units": 10, "base_price": 43},
    "Granddaddy Purple": {"base_effects": {"Sedating"},  "craft_cost": 45,  "yield_units": 10, "base_price": 44},
    "Meth":              {"base_effects": set(),         "craft_cost": 140, "yield_units": 10, "base_price": 70},
    "Cocaine":           {"base_effects": set(),         "craft_cost": 245, "yield_units": 10, "base_price": 150},
}

INGREDIENTS = {
    "Banana":       {"cost": 8,  "add": "Gingeritis",       "replace": {}},
    "Cuke":         {"cost": 2,  "add": "Energizing",       "replace": {}},
    "Donut":        {"cost": 3,  "add": "Calorie-Dense",    "replace": {}},
    "Battery":      {"cost": 2,  "add": "Bright-Eyed",      "replace": {}},
    "Paracetamol":  {"cost": 3,  "add": "Sneaky",           "replace": {"Munchies": "Anti-Gravity"}},
    "Gasoline":     {"cost": 5,  "add": "Toxic",            "replace": {"Sedating": "Munchies"}},
    "Mouth Wash":   {"cost": 4,  "add": "Balding",          "replace": {}},
    "Energy Drink": {"cost": 6,  "add": None,               "replace": {"Balding": "Schizophrenic", "Foggy": "Laxative"}},
    "Mega Bean":    {"cost": 7,  "add": "Foggy",            "replace": {}},
    "Motor Oil":    {"cost": 6,  "add": "Slippery",         "replace": {"Energizing": "Schizophrenic"}},
    "Iodine":       {"cost": 8,  "add": "Jennerising",      "replace": {}},
    "Horse Semen":  {"cost": 9,  "add": "Long-Faced",       "replace": {}},
    "Chili":        {"cost": 7,  "add": "Spicy",            "replace": {}},
    "Flu Medicine": {"cost": 5,  "add": None,               "replace": {"Euphoric": "Laxative"}},
    "Addy":         {"cost": 9,  "add": "Thought-Provoking","replace": {}},
    "Viagra":       {"cost": 4,  "add": "Tropic Thunder",   "replace": {}},
}

EFFECT_MULTIPLIERS = {
    "Shrinking":       0.60, "Zombifying":     0.58, "Cyclopean":      0.56,
    "Anti-Gravity":    0.54, "Glowing":        0.50, "Electrifying":   0.50,
    "Long-Faced":      0.45, "Tropic Thunder": 0.42, "Bright-Eyed":    0.40,
    "Thought-Provoking":0.38,"Calorie-Dense":  0.28, "Energizing":     0.22,
    "Gingeritis":      0.12, "Spicy":          0.08,
}

ALL_EFFECTS = (
    list(EFFECT_MULTIPLIERS.keys())
    + [
        "Munchies","Sneaky","Toxic","Balding","Schizophrenic",
        "Foggy","Jennerising","Laxative","Euphoric","Slippery",
        "Sedating"            
    ]
)

MAX_EFFECTS = 8  

DRUG_MAP       = {name.lower(): name for name in BASE_DRUGS}
EFFECT_MAP = {eff.lower(): eff for eff in ALL_EFFECTS}
INGREDIENT_MAP = {name.lower(): name for name in INGREDIENTS}

def validate_drug(x):
    key = x.lower()
    if key not in DRUG_MAP:
        raise argparse.ArgumentTypeError(f"Invalid drug '{x}'. Valid: {', '.join(BASE_DRUGS)}")
    return DRUG_MAP[key]

def validate_effect(x):
    key = x.lower()
    if key not in EFFECT_MAP:
        raise argparse.ArgumentTypeError(f"Invalid effect '{x}'. Valid: {', '.join(EFFECT_MULTIPLIERS)}")
    return EFFECT_MAP[key]

def validate_ingredient(x):
    key = x.lower()
    if key not in INGREDIENT_MAP:
        raise argparse.ArgumentTypeError(f"Invalid ingredient '{x}'. Valid: {', '.join(INGREDIENTS)}")
    return INGREDIENT_MAP[key]

def apply_ingredient(effects, ingredient):
    rules = INGREDIENTS[ingredient]
    new = set(effects)

    for old, new_eff in rules["replace"].items():
        if old in new:
            new.remove(old)
            new.add(new_eff)
            return frozenset(new)

    if rules["add"]:
        new.add(rules["add"])
    return frozenset(new)

def find_recipe(base_eff, target_eff, debug=False):
    start = frozenset(base_eff)
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        effects, path = queue.popleft()
        for ing in INGREDIENTS:
            new_eff = apply_ingredient(effects, ing)
            if len(new_eff) > MAX_EFFECTS:
                continue
            new_path = path + [ing]
            if debug:
                print(f"[DEBUG] Mix {' -> '.join(new_path)} -> Effects={new_eff}")
            if target_eff.issubset(new_eff):
                return new_path
            if new_eff not in seen:
                seen.add(new_eff)
                queue.append((new_eff, new_path))
    return None

def calculate_price_and_profit(drug, recipe):
    base = BASE_DRUGS[drug]
    cost = base["craft_cost"] + sum(INGREDIENTS[i]["cost"] for i in recipe)
    effs = set(base["base_effects"])
    for i in recipe:
        effs = set(apply_ingredient(effs, i))

    multiplier = sum(EFFECT_MULTIPLIERS.get(e, 0) for e in effs)
    unit_price = base["base_price"] * (1 + multiplier)
    revenue   = unit_price * base["yield_units"]
    profit    = revenue - cost
    return cost, revenue, profit, effs, unit_price

def main():
    parser = argparse.ArgumentParser(
        description="Find or evaluate mixes for Schedule I"
    )
    parser.add_argument(
        "--drug", '-d', required=True, type=validate_drug,
        help="Base drug (case-insensitive)"
    )
    parser.add_argument(
        "--effects", '-e', nargs="+", type=validate_effect,
        help="Desired effects to search for (case-insensitive)"
    )
    parser.add_argument(
        "--ingredients", '-i', nargs="+", type=validate_ingredient,
        help="Custom ingredients to evaluate (case-insensitive)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Show BFS debug trace"
    )
    args = parser.parse_args()

    if not args.effects and not args.ingredients:
        parser.error("Must specify at least one of --effects or --ingredients.")

    output = []

    if args.effects:
        if len(args.effects) > MAX_EFFECTS:
            parser.error(f"Cannot target more than {MAX_EFFECTS} effects.")
        recipe = find_recipe(BASE_DRUGS[args.drug]["base_effects"], set(args.effects), debug=args.debug)
        if recipe:
            cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, recipe)
            output.append(f"Recipe found for effects: {', '.join(args.effects)}")
            output.append(f"Mix steps: {' -> '.join(recipe)}")
            output.append(f"Profit: ${prof:.2f}  (Unit price ${unit:.2f}, cost ${cost:.2f})\n")
        else:
            output.append("No recipe found for those effects (cap 8). Try --debug.\n")

    if args.ingredients:
        cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, args.ingredients)
        output.append("Evaluating custom ingredients:")
        output.append(f"Mix steps: {' -> '.join(args.ingredients)}")
        output.append(f"Final Effects: {', '.join(final)}")
        output.append(f"Profit: ${prof:.2f} \n(Unit price ${unit:.2f}, cost ${cost:.2f})\n")

    full_output = "\n".join(output).strip()
    print(full_output)

    save = input("Save results to file? (y/n): ").strip().lower()
    if save in ("y", "yes"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{args.drug.replace(' ', '_')}_{ts}.txt"
        with open(fname, "w") as f:
            f.write(full_output)
        print(f"Results saved to {fname}")

if __name__ == "__main__":
    main()
