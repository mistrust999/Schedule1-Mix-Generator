import argparse
from collections import deque
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

EFFECT_VALUES = {
    "Gingeritis":12,   "Energizing":10,     "Calorie-Dense":8,   "Bright-Eyed":10,
    "Anti-Gravity":25, "Munchies":5,        "Slippery":7,        "Balding":9,
    "Schizophrenic":22,"Foggy":11,          "Long-Faced":15,     "Jennerising":13,
    "Spicy":8,         "Laxative":9,        "Euphoric":14,       "Thought-Provoking":14,
    "Tropic Thunder":12,"Sneaky":11,        "Toxic":10
}

MAX_EFFECTS = 8  

DRUG_MAP       = {name.lower(): name for name in BASE_DRUGS}
EFFECT_MAP     = {name.lower(): name for name in EFFECT_VALUES}
INGREDIENT_MAP = {name.lower(): name for name in INGREDIENTS}

def validate_drug(x):
    key = x.lower()
    if key not in DRUG_MAP:
        raise argparse.ArgumentTypeError(f"Invalid drug '{x}'. Valid: {', '.join(BASE_DRUGS)}")
    return DRUG_MAP[key]

def validate_effect(x):
    key = x.lower()
    if key not in EFFECT_MAP:
        raise argparse.ArgumentTypeError(f"Invalid effect '{x}'. Valid: {', '.join(EFFECT_VALUES)}")
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
                print(f"[DEBUG] Mix {' â†’ '.join(new_path)} â†’ Effects={new_eff}")
            if target_eff.issubset(new_eff):
                return new_path
            if new_eff not in seen:
                seen.add(new_eff)
                queue.append((new_eff, new_path))
    return None

def calculate_price_and_profit(drug, recipe):
    base = BASE_DRUGS[drug]
    cost   = base["craft_cost"] + sum(INGREDIENTS[i]["cost"] for i in recipe)
    effs   = set(base["base_effects"])
    for i in recipe:
        effs = set(apply_ingredient(effs, i))
    unit   = base["base_price"] + sum(EFFECT_VALUES[e] for e in effs)
    rev    = unit * base["yield_units"]
    prof   = rev - cost
    return cost, rev, prof, effs, unit

def main():
    parser = argparse.ArgumentParser(
        description="Find or evaluate a mix in Schedule I"
    )
    parser.add_argument(
        "--drug", required=True, type=validate_drug,
        help="Base drug (case-insensitive)"
    )
    parser.add_argument(
        "--effects", nargs="+", type=validate_effect,
        help="Desired effects to search for (case-insensitive)"
    )
    parser.add_argument(
        "--ingredients", nargs="+", type=validate_ingredient,
        help="Custom ingredient list to evaluate (case-insensitive)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print each mix step and resulting effects"
    )
    args = parser.parse_args()

    if not args.effects and not args.ingredients:
        parser.error("Must specify at least one of --effects or --ingredients.")

    if args.effects:
        if len(args.effects) > MAX_EFFECTS:
            parser.error(f"Cannot target more than {MAX_EFFECTS} effects.")
        recipe = find_recipe(BASE_DRUGS[args.drug]["base_effects"], set(args.effects), debug=args.debug)
        if recipe:
            print("Recipe for effects:", " -> ".join(args.effects))
            print("Mix steps:   ", " -> ".join(recipe))
            cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, recipe)
            print(f"Profit: ${prof:.2f} (Unit price ${unit:.2f}, cost ${cost:.2f})\n")
        else:
            print("No recipe found for effects (cap 8). Try --debug.\n")

    if args.ingredients:
        recipe = args.ingredients
        print("Evaluating custom ingredients:")
        print("Mix steps:   ", " -> ".join(recipe))
        cost, rev, prof, final, unit = calculate_price_and_profit(args.drug, recipe)
        print(textwrap.dedent(f"""\
            Final Effects:     {', '.join(final)}
            Crafting Cost:     ${cost:.2f}
            Estimated Unit $:  ${unit:.2f}
            Total Revenue:     ${rev:.2f}
            Estimated Profit:  ${prof:.2f}
        """))

if __name__ == "__main__":
    main()
