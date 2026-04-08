// Pizza data for April 2026 (from Arizmendi's website)
// Days are 0-indexed (0 = Sunday, 1 = Monday, etc.)
// Closed on Mondays

const PIZZA_DATA = {
    // April 2026
    "2026-04-01": "roasted yellow potatoes, spinach, sharp cheddar, rosemary oil, parmesan",
    "2026-04-02": "caramelized onions, shiitake mushrooms, gruyere cheese, garlic oil, p&p",
    "2026-04-03": "spinach, kalamata olives, feta cheese, lemon olive oil, p&p",
    "2026-04-04": "mushrooms, scallions, white cheddar, thyme oil, p&p",
    "2026-04-05": "house-made tomato sauce, spinach, fontina, garlic oil, p&p",
    // Monday 2026-04-06 - CLOSED
    "2026-04-07": "roasted yellow potatoes, spinach, sharp cheddar, garlic oil, parmesan",
    "2026-04-08": "mushrooms, fresh herbs, feta, lemon-garlic oil, p&p",
    "2026-04-09": "fresh asparagus, red onion, goat cheese, lemon vinaigrette",
    "2026-04-10": "shiitake, button and portabella mushrooms with sesame-ginger-garlic vinaigrette, parsley",
    "2026-04-11": "'Quattro Fromaggio' house-made sauce w/asiago, feta, parmesan & romano, thyme oil, parsley",
    "2026-04-12": "mixed cherry tomatoes, spinach, basil pesto",
    // Monday 2026-04-13 - CLOSED
    "2026-04-14": "cherry tomatoes, poblano peppers, feta cheese, lime oil, parsley & parmesan",
    "2026-04-15": "broccoli, roasted garlic, white cheddar, thyme oil, p&p",
    "2026-04-16": "marinated artichoke hearts, spinach, fontina, garlic oil, parmesan",
    "2026-04-17": "mushrooms, scallions, gruyere, rosemary oil, p&p",
    "2026-04-18": "cherry tomatoes with basil pesto",
    "2026-04-19": "house-made tomato sauce, feta, fontina, garlic oil, p&p",
    // Monday 2026-04-20 - CLOSED
    "2026-04-21": "caramelized onions, spinach, gruyere, garlic oil, parmesan",
    "2026-04-22": "red onions, spinach, feta, balsamic vinaigrette",
    "2026-04-23": "mushrooms, red onions, goat cheese, garlic oil, p&p",
    "2026-04-24": "cherry tomatoes with basil pesto",
    "2026-04-25": "house-made tomato sauce, spinach, fontina, rosemary oil, p&p",
    "2026-04-26": "shiitake, portabella and button mushrooms with sesame-ginger-garlic vinaigrette",
    // Monday 2026-04-27 - CLOSED
    "2026-04-28": "house-made tomato sauce, gruyere, feta, garlic oil, p&p",
    "2026-04-29": "cherry tomatoes, roasted garlic, fontina, rosemary oil, p&p",
    "2026-04-30": "roasted yellow potatoes, masala curry, spinach, garlic oil",
    
    // May 2026 (placeholder - would need to be updated monthly)
    // May 1 is International Workers' Day - CLOSED
    "2026-05-01": "CLOSED - International Workers' Day",
    "2026-05-02": "TBD - Check website for May menu",
    "2026-05-03": "TBD - Check website for May menu",
};

// Special closures (beyond regular Monday closures)
const SPECIAL_CLOSURES = {
    "2026-05-01": "International Workers' Day"
};
