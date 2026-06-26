import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image


load_dotenv()

st.set_page_config(
	page_title="FitGen AI - Personalized Workout & Diet Planner",
	page_icon="/assets/logo.png",
	layout="wide",
	initial_sidebar_state="expanded",
)


def inject_styles() -> None:
	st.markdown(
		"""
		<style>
		:root {
			--bg: #f4f7fb;
			--panel: rgba(255, 255, 255, 0.84);
			--panel-border: rgba(15, 23, 42, 0.08);
			--text: #0f172a;
			--muted: #5b6476;
			--accent: #0ea5a6;
			--accent-dark: #0f766e;
			--shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
		}

		.stApp {
			background:
				radial-gradient(circle at top left, rgba(14, 165, 166, 0.12), transparent 30%),
				radial-gradient(circle at top right, rgba(59, 130, 246, 0.10), transparent 24%),
				linear-gradient(180deg, #f8fbfd 0%, #eef4f8 100%);
			color: var(--text);
		}

		.main-header {
			padding: 1.4rem 1.5rem;
			border: 1px solid var(--panel-border);
			border-radius: 24px;
			background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(246, 250, 253, 0.88));
			box-shadow: var(--shadow);
			margin-bottom: 1rem;
		}

		.eyebrow {
			text-transform: uppercase;
			letter-spacing: 0.18em;
			font-size: 0.72rem;
			color: var(--accent-dark);
			font-weight: 700;
			margin-bottom: 0.4rem;
		}

		.title {
			font-size: 2.2rem;
			font-weight: 800;
			line-height: 1.1;
			margin-bottom: 0.5rem;
			color: var(--text);
		}

		.subtitle {
			color: var(--muted);
			font-size: 1rem;
			max-width: 760px;
		}

		.card {
			background: var(--panel);
			border: 1px solid var(--panel-border);
			box-shadow: var(--shadow);
			border-radius: 22px;
			padding: 1.2rem 1.25rem;
		}

		.metric-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
			gap: 0.8rem;
			margin-top: 1rem;
		}

		.metric {
			background: rgba(255, 255, 255, 0.92);
			border: 1px solid var(--panel-border);
			border-radius: 18px;
			padding: 0.9rem 1rem;
		}

		.metric-label {
			color: var(--muted);
			font-size: 0.78rem;
			text-transform: uppercase;
			letter-spacing: 0.08em;
			margin-bottom: 0.3rem;
		}

		.metric-value {
			color: var(--text);
			font-size: 1rem;
			font-weight: 700;
		}

		.stButton > button {
			background: linear-gradient(135deg, var(--accent), #3b82f6) !important;
			color: white !important;
			border: 0 !important;
			border-radius: 14px !important;
			padding: 0.7rem 1.15rem !important;
			font-weight: 700 !important;
			box-shadow: 0 10px 22px rgba(14, 165, 166, 0.24) !important;
		}

		.stDownloadButton > button {
			background: white !important;
			color: var(--text) !important;
			border: 1px solid var(--panel-border) !important;
			border-radius: 14px !important;
			padding: 0.7rem 1.15rem !important;
			font-weight: 700 !important;
		}

		.stTextInput input,
		.stNumberInput input,
		.stTextArea textarea,
		.stSelectbox div[data-baseweb="select"] > div,
		.stSlider [data-baseweb="slider"] {
			border-radius: 14px !important;
		}

		.section-title {
			margin: 0.25rem 0 0.5rem;
			font-size: 1.1rem;
			font-weight: 750;
			color: var(--text);
		}

		.footer-note {
			color: var(--muted);
			font-size: 0.85rem;
			margin-top: 0.75rem;
		}
		</style>
		""",
		unsafe_allow_html=True,
	)


def load_logo() -> Image.Image | None:
	logo_path = os.path.join("assets", "logo.png")
	try:
		return Image.open(logo_path)
	except Exception:
		return None


def build_prompt(data: dict[str, str]) -> str:
	return f"""You are FitGen AI, a certified-style fitness and nutrition planning assistant.

Create a personalized workout and diet plan using the user's profile below. Respond in clean markdown only.

User Profile:
- Name: {data['name']}
- Age: {data['age']}
- Gender: {data['gender']}
- Height: {data['height']} cm
- Weight: {data['weight']} kg
- Fitness Goal: {data['fitness_goal']}
- Diet Preference: {data['diet_preference']}
- Activity Level: {data['activity_level']}
- Workout Days per Week: {data['workout_days']}
- Medical Conditions: {data['medical_conditions']}

Requirements for the response:
- Include these exact sections in this order:
  1. Personalized Workout Plan
  2. Weekly Schedule
  3. Diet Plan
  4. Estimated Daily Calories
  5. Protein Recommendation
  6. Water Intake
  7. Sleep Recommendation
  8. Lifestyle Tips
  9. Motivation
  10. Medical Disclaimer
- Make the workout realistic for the user's goal, activity level, age, height, weight, and workout days.
- Adapt the diet to the specified food preference.
- If medical conditions are provided, include conservative guidance and encourage medical clearance where appropriate.
- Give practical, specific recommendations using bullets and short paragraphs.
- Provide calorie and protein targets as estimated ranges, not exact medical prescriptions.
- Include a concise, safety-minded medical disclaimer at the end.
- Keep the tone encouraging, expert, and clear.
"""


def extract_text(response: object) -> str:
	text = getattr(response, "text", None)
	if text:
		return text.strip()

	candidates = getattr(response, "candidates", None) or []
	for candidate in candidates:
		content = getattr(candidate, "content", None)
		parts = getattr(content, "parts", None) or []
		for part in parts:
			part_text = getattr(part, "text", None)
			if part_text:
				return part_text.strip()

	return ""


def generate_plan(data: dict[str, str]) -> str:
	api_key = os.getenv("GEMINI_API_KEY")
	if not api_key:
		raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

	client = genai.Client(api_key=api_key)
	response = client.models.generate_content(
		model="gemini-2.5-flash",
		contents=build_prompt(data),
	)
	plan = extract_text(response)
	if not plan:
		raise RuntimeError("The model returned an empty response.")
	return plan


def render_profile_card(profile: dict[str, str]) -> None:
	st.markdown(
		f"""
		<div class="card">
			<div class="section-title">Your Profile Snapshot</div>
			<div class="metric-grid">
				<div class="metric"><div class="metric-label">Name</div><div class="metric-value">{profile['name']}</div></div>
				<div class="metric"><div class="metric-label">Goal</div><div class="metric-value">{profile['fitness_goal']}</div></div>
				<div class="metric"><div class="metric-label">Activity</div><div class="metric-value">{profile['activity_level']}</div></div>
				<div class="metric"><div class="metric-label">Workout Days</div><div class="metric-value">{profile['workout_days']} per week</div></div>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)


def main() -> None:
	inject_styles()

	logo = load_logo()
	left, right = st.columns([0.8, 2.2], vertical_alignment="center")
	with left:
		if logo is not None:
			st.image(logo, use_container_width=True)
		else:
			st.markdown("<div class='card'><div class='title'>FitGen AI</div></div>", unsafe_allow_html=True)

	with right:
		st.markdown(
			"""
			<div class="main-header">
				<div class="eyebrow">Personalized fitness planning</div>
				<div class="title">FitGen AI - Personalized Workout & Diet Planner</div>
				<div class="subtitle">
					Generate a structured workout, nutrition, and lifestyle plan tailored to your body profile,
					goals, diet choice, activity level, and weekly training capacity.
				</div>
			</div>
			""",
			unsafe_allow_html=True,
		)

	st.sidebar.title("Build Your Plan")
	st.sidebar.caption("Enter your details to generate a personalized plan.")

	if not os.getenv("GEMINI_API_KEY"):
		st.sidebar.warning("Add GEMINI_API_KEY to your .env file before generating a plan.")

	with st.sidebar.form("planner_form"):
		name = st.text_input("Name", placeholder="Enter your name")
		age = st.number_input("Age", min_value=10, max_value=100, value=25, step=1)
		gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
		height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
		weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
		fitness_goal = st.selectbox(
			"Fitness Goal",
			["Lose Fat", "Build Muscle", "Maintain Weight", "Increase Stamina"],
		)
		diet_preference = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"])
		activity_level = st.selectbox(
			"Activity Level",
			["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Athlete"],
		)
		workout_days = st.slider("Workout Days per Week", min_value=1, max_value=7, value=5)
		medical_conditions = st.text_area(
			"Medical Conditions (optional)",
			placeholder="Examples: knee pain, hypertension, asthma, diabetes, back pain",
			height=120,
		)
		submitted = st.form_submit_button("Generate My Plan")

	if submitted:
		if not name.strip():
			st.error("Please enter your name to generate a plan.")
		else:
			user_data = {
				"name": name.strip(),
				"age": str(age),
				"gender": gender,
				"height": f"{height:.1f}",
				"weight": f"{weight:.1f}",
				"fitness_goal": fitness_goal,
				"diet_preference": diet_preference,
				"activity_level": activity_level,
				"workout_days": str(workout_days),
				"medical_conditions": medical_conditions.strip() or "None provided",
			}

			with st.spinner("Generating your personalized workout and diet plan..."):
				try:
					plan = generate_plan(user_data)
					st.session_state["generated_plan"] = plan
					st.session_state["generated_profile"] = user_data
					st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
					st.success("Your plan is ready.")
				except Exception as exc:
					st.session_state.pop("generated_plan", None)
					st.session_state.pop("generated_profile", None)
					st.error(f"Unable to generate a plan: {exc}")

	if "generated_plan" in st.session_state:
		st.markdown("<div class='section-title'>Plan Preview</div>", unsafe_allow_html=True)
		profile = st.session_state.get("generated_profile", {})
		if profile:
			render_profile_card(profile)

		st.markdown(st.session_state["generated_plan"], unsafe_allow_html=False)

		file_name = "fitgen-ai-plan.md"
		if profile.get("name"):
			file_name = f"fitgen-ai-plan-{profile['name'].lower().replace(' ', '-')}.md"

		st.download_button(
			label="Download Plan",
			data=st.session_state["generated_plan"],
			file_name=file_name,
			mime="text/markdown",
		)

	st.markdown(
		"<div class='footer-note'>FitGen AI provides general fitness guidance and does not replace professional medical advice.</div>",
		unsafe_allow_html=True,
	)


if __name__ == "__main__":
	main()
