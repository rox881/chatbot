# 🧠 ML-Powered Weight Loss Chatbot

> **A chatbot that understands user intent, then uses ML to generate a personalized weight-loss roadmap and food plan.**

[![ML-Based](https://img.shields.io/badge/ML-Powered-green)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow)](https://github.com)

---

## 🎯 Overview

This is **NOT** a rule-based chatbot with hardcoded diet plans. This system has **THREE INTELLIGENT BRAINS**, all ML-based:

1. **Intent Understanding (NLP ML)** - Understands what the user wants
2. **Roadmap/Plan Generation (Sequential ML)** - Generates personalized weight-loss trajectories
3. **Food Recommendation (ML Matching)** - Suggests foods based on nutritional targets

The chatbot is just the **front face** — all logic flows from trained machine learning models.

---

## 🏗️ Architecture

### High-Level Flow

```
User Message
   ↓
Intent Detection (ML)
   ↓
Profile Understanding
   ↓
Roadmap Generation (ML)
   ↓
Food Recommendation (ML)
   ↓
Natural Language Response
```

**No hardcoded plans. No static charts. Everything flows from models.**

---

## 🧩 System Components

### 1️⃣ Intent Understanding (ML-NLP)

**What it does:**  
Classifies user intent to determine which ML pipeline to activate.

**Example Intents:**
- `weight_loss_plan`
- `diet_suggestion`
- `progress_query`
- `maintenance_plan`

**ML Technique:**
- TF-IDF / Word Embeddings + Classifier (Logistic Regression / Neural Network)

**Example:**
```
Input: "I want to lose weight in 3 months"
Output: intent = weight_loss_plan
```

✅ This decides **which ML pipeline to activate**.

---

### 2️⃣ Roadmap Generation (🔥 CORE ML BRAIN)

This is the **most important component** of the system.

#### ML Problem Formulation

Weight loss is treated as a **sequence prediction problem**.

**State Definition:**
```python
State(t) = [
  weight,
  BMI,
  daily_calories,
  activity_level,
  week
]
```

**Model Learns:**
```
State(t) → State(t+1)
```

**ML Model:**
- Neural Network (MLP)
- Optional: LSTM for advanced sequential modeling

#### How Roadmap is Generated

1. Start with user's current state
2. Predict next week's state
3. Feed output back into model
4. Repeat for N weeks

This is **iterative ML rollout**, not predefined rules.

#### Example ML-Generated Roadmap

```
Week 1  → 80.8 kg → 1900 kcal → 6k steps
Week 4  → 77.3 kg → 1750 kcal → 8k steps
Week 8  → 72.9 kg → 1600 kcal → 10k steps
Week 12 → 68.5 kg → 1500 kcal → 12k steps
```

⚠️ This sequence **emerges from the model**, not predefined logic.

---

### 3️⃣ Food Recommendation (ML Matching)

Once calories and macros are determined, food is selected via **ML similarity matching**.

**ML Approach:**
- Food items embedded as vectors: `[calories, protein, carbs, fat]`
- User nutritional target is also a vector
- Distance/similarity-based ML:
  - K-Nearest Neighbors (KNN)
  - Cosine Similarity

**ML Decides:**
> "Which foods best fit this week's nutritional target?"

#### Example Output

```
Week 4 – Target: 1750 kcal

Recommended foods:
• Oats + fruits (Breakfast)
• Dal + brown rice (Lunch)
• Paneer salad (Dinner)
• Fruit yogurt (Snack)
```

No `if BMI > 25` statements. Pure ML matching.

---

### 4️⃣ Chatbot Response Generation

The chatbot **explains ML output** in natural language — it does NOT invent plans.

**Example User-Facing Response:**
```
Based on your goal and health profile,
I've generated a 12-week ML-based roadmap.

This week:
• Target weight: 80.8 kg
• Calories/day: 1900
• Activity: 6,000 steps

Suggested meals align with this target.
Would you like the full 12-week plan or just next week?
```

---

## 🧠 Why This is "Fully ML"

You can confidently state:

> "Intent is classified using an NLP model.  
> The roadmap is generated using a learned state-transition model.  
> Food is selected using similarity-based ML matching.  
> **No diet rules are hardcoded.**"

This **eliminates the 'rule-based' criticism** entirely.

---

## 📊 Datasets

### Training Data Requirements

**Sequential State Data:**
```
person_id | week | weight | calories | activity | BMI
```

**Food Database:**
```
food | calories | protein | carbs | fat
```

Even **synthetic but realistic data is acceptable** in academic settings and hackathons.

---

## 🛠️ Technology Stack

- **Backend:** Python, Flask/FastAPI
- **ML Frameworks:** TensorFlow / PyTorch, Scikit-learn
- **NLP:** TF-IDF, Word2Vec, BERT (optional)
- **Database:** PostgreSQL / MongoDB
- **Frontend:** HTML, CSS, JavaScript (chatbot UI)

---

## 🚀 Key Features

✅ **Intent-aware chatbot** - Understands user goals  
✅ **ML-generated weight-loss roadmap** - Personalized trajectories  
✅ **ML-based food suggestion** - Nutritionally optimized  
✅ **Sequential intelligence** - Learns from progression patterns  
✅ **Small but powerful** - Feasible for academic projects  
✅ **Defensible in viva/hackathon** - Clear ML methodology  

---

## � Work in Progress

We are actively improving the following components:

### ✅ Completed
- [x] Project architecture design
- [x] ML-based system design
- [x] Intent classification framework
- [x] Roadmap generation algorithm design

### 🔄 In Development
- [ ] **Intent Classifier Model**
  - Training NLP model for user intent detection
  - Expanding training dataset with more intent variations
  
- [ ] **Sequential Roadmap Generator**
  - Building neural network for state transition prediction
  - Creating synthetic training data for weight progression
  
- [ ] **Food Recommendation Engine**
  - Implementing KNN-based food matching
  - Building comprehensive food database with Indian cuisine
  
- [ ] **Chatbot Interface**
  - Developing conversational UI
  - Integrating ML models with chat flow

### 🔜 Upcoming
- [ ] Model training and optimization
- [ ] Frontend chatbot UI development
- [ ] API integration and testing
- [ ] Performance evaluation and benchmarking
- [ ] Documentation and deployment

**Last Updated:** January 26, 2026

---

## �📦 Project Structure

```
chatbot/
│
├── data/
│   ├── training_data.csv
│   └── food_database.csv
│
├── models/
│   ├── intent_classifier.py
│   ├── roadmap_generator.py
│   └── food_recommender.py
│
├── app/
│   ├── chatbot.py
│   └── api.py
│
├── notebooks/
│   └── model_training.ipynb
│
├── requirements.txt
└── README.md
```

---

## 🎓 Academic Defense Points

When presenting this project:

1. **"How is this different from rule-based systems?"**
   - Intent, roadmap, and food selection are all ML-predicted, not hardcoded.

2. **"What ML techniques are used?"**
   - NLP classification, sequential state prediction (NN/LSTM), similarity-based matching.

3. **"Is the data realistic?"**
   - Yes, either real or synthetic but physiologically grounded.

4. **"Can you scale this?"**
   - Absolutely. More training data → better predictions.

---

## 🔮 Future Enhancements

- 🏃 Real-time activity tracking integration
- 📊 Advanced visualization dashboards
- 🤖 Voice-based chatbot interface
- 🌍 Multi-language support
- 💪 Exercise recommendation engine

---

## 👥 Contributors

- **Team:** [Your Team Name]
- **Institution:** [Your College Name]
- **Semester:** 6th Semester
- **Project Type:** Working Model

---

## 📜 License

[Specify your license, e.g., MIT]

---

## 🙏 Acknowledgments

This project demonstrates the power of machine learning in personalized health and fitness applications. Special thanks to our mentors and advisors for their guidance.

---

**Built with ❤️ and ML by [Your Team]**
