# FitGen AI - Personalized Workout & Diet Planner

FitGen AI is a Streamlit application that generates a personalized workout and diet plan using Gemini.

## Features

- Modern Streamlit interface with a logo from `assets/logo.png`
- Collects personal, fitness, diet, and medical context
- Uses the Google Gen AI SDK with `gemini-2.5-flash`
- Displays a markdown plan with a download option
- Shows a spinner while the plan is being generated

## Setup

1. Create a `.env` file in the project root.
2. Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

## Notes

- Height is collected in centimeters and weight in kilograms.
- Medical conditions are optional, but including them helps the plan become safer and more realistic.
- The generated plan includes a medical disclaimer and should not replace professional guidance.