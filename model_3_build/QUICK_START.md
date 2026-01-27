# Quick Start Guide - Model 3 Food Recommender

## How to Run Manual Tests

### Step 1: Open Terminal/Command Prompt

Navigate to the Model 3 directory:
```bash
cd "c:\Users\Gaurav\OneDrive\CollageMINi\6th sem\dataset\nlp\MODEL 3\model_3_build"
```

### Step 2: Run the Manual Test Script

```bash
python manual_test.py
```

This will automatically run 4 sample test cases:
- **Sample 1**: Weight loss (1842 cal, no restrictions)
- **Sample 2**: Muscle gain (2590 cal, vegetarian)
- **Sample 3**: Maintenance (2100 cal, no dairy & nuts)
- **Sample 4**: Custom test (2000 cal, vegan) - YOU CAN MODIFY THIS!

---

## How to Test Your Own Inputs

### Option A: Modify manual_test.py

Open `manual_test.py` and find lines 121-125:

```python
custom_input = {
    "target_calories": 2000,        # Change this value
    "fitness_goal": "weight_loss",  # Change to: weight_loss, muscle_gain, or maintenance
    "dietary_restrictions": ["vegan"]  # Add your restrictions here
}
```

Change the values and run:
```bash
python manual_test.py
```

### Option B: Create Your Own Test File

Create a new file called `my_test.py`:

```python
from model3_food_recommender import FoodRecommender

# Initialize
recommender = FoodRecommender('model3_food_database.json')

# YOUR INPUT HERE
my_input = {
    "target_calories": 2200,
    "fitness_goal": "muscle_gain",
    "dietary_restrictions": ["vegetarian", "no_dairy"]
}

# Generate plan
result = recommender.generate_plan(my_input)

# Print results
if result['status'] == 'success':
    print(result['chatbot_message'])
    print("\n--- DETAILED BREAKDOWN ---")
    for meal_name in ['breakfast', 'lunch', 'dinner', 'snack']:
        meal = result['meal_plan'][meal_name]
        print(f"\n{meal_name.upper()}:")
        for food in meal['foods']:
            print(f"  - {food['name']}: {food['portion_g']}g")
else:
    print(f"ERROR: {result['error']}")
```

Then run:
```bash
python my_test.py
```

---

## Available Options

### Fitness Goals (choose one):
- `"weight_loss"` - High protein (35%), moderate carbs (40%), low fat (25%)
- `"muscle_gain"` - Moderate protein (30%), high carbs (50%), low fat (20%)
- `"maintenance"` - Balanced (25% protein, 45% carbs, 30% fat)

### Dietary Restrictions (can use multiple):
- `"vegetarian"` - No meat/fish/poultry
- `"vegan"` - No animal products
- `"no_dairy"` - No milk/yogurt/cheese
- `"no_nuts"` - No tree nuts or peanuts
- `"no_eggs"` - No eggs
- `"no_fish"` - No fish/seafood
- `"no_gluten"` - No wheat/gluten
- `"no_soy"` - No soy products

Examples:
```python
"dietary_restrictions": []  # No restrictions
"dietary_restrictions": ["vegetarian"]  # Just vegetarian
"dietary_restrictions": ["vegan"]  # Vegan (strictest)
"dietary_restrictions": ["no_dairy", "no_nuts"]  # Multiple restrictions
```

---

## Sample Test Inputs

### 1. Weight Loss - High Protein
```python
{
    "target_calories": 1600,
    "fitness_goal": "weight_loss",
    "dietary_restrictions": []
}
```

### 2. Muscle Gain - Vegetarian
```python
{
    "target_calories": 2800,
    "fitness_goal": "muscle_gain",
    "dietary_restrictions": ["vegetarian"]
}
```

### 3. Maintenance - Vegan
```python
{
    "target_calories": 2200,
    "fitness_goal": "maintenance",
    "dietary_restrictions": ["vegan"]
}
```

### 4. Weight Loss - Multiple Restrictions
```python
{
    "target_calories": 1800,
    "fitness_goal": "weight_loss",
    "dietary_restrictions": ["no_dairy", "no_gluten", "no_fish"]
}
```

### 5. Muscle Gain - High Calories
```python
{
    "target_calories": 3200,
    "fitness_goal": "muscle_gain",
    "dietary_restrictions": []
}
```

---

## Understanding the Output

### Chatbot Message
Human-readable text that can be sent directly to users

### Detailed Meal Plan
- Shows each meal (breakfast, lunch, dinner, snack)
- Lists all foods and their portions in grams
- Shows nutritional breakdown per meal

### Daily Summary
- Total calories generated
- Total protein, carbs, fat in grams
- Macro accuracy percentage

---

## Quick Python Interactive Test

Open Python in the terminal:
```bash
python
```

Then run:
```python
from model3_food_recommender import FoodRecommender
recommender = FoodRecommender('model3_food_database.json')

# Test 1: Simple weight loss
result = recommender.generate_plan({
    "target_calories": 1800,
    "fitness_goal": "weight_loss",
    "dietary_restrictions": []
})
print(result['chatbot_message'])

# Test 2: Vegan muscle gain
result2 = recommender.generate_plan({
    "target_calories": 2500,
    "fitness_goal": "muscle_gain",
    "dietary_restrictions": ["vegan"]
})
print(result2['chatbot_message'])
```

---

## Troubleshooting

### Error: "FileNotFoundError"
Make sure you're in the correct directory where `model3_food_database.json` exists.

### Error: "Invalid goal"
Check that fitness_goal is one of: "weight_loss", "muscle_gain", "maintenance"

### Error: "Safety validation failed"
This means the generated plan doesn't meet safety requirements (usually protein minimum).
Try different calorie values or fewer restrictions.

---

## Where are the files?

All files are in:
```
c:\Users\Gaurav\OneDrive\CollageMINi\6th sem\dataset\nlp\MODEL 3\model_3_build\
```

Key files:
- `model3_food_recommender.py` - Main implementation
- `model3_food_database.json` - Food database (53 items)
- `manual_test.py` - Manual testing script (RECOMMENDED)
- `test_model3.py` - Automated comprehensive tests
- `README.md` - Documentation

---

Enjoy testing your Food Recommendation Engine! 🍎🥗🍗
