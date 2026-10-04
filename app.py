import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.title("TripSaathi")
st.write("A trip itinerary draft you can adjust to your preferences.")

destination = st.text_input("Where do you want to go?")
days = st.number_input("How many days?", min_value=1, max_value=14, value=2)
budget = st.number_input("Budget", min_value=10)
interests = st.text_input("What do you enjoy?", placeholder="Food, history, nature...")
must_avoid = st.text_input(
    "Must avoid (optional)",
    placeholder="Crowded places, long treks, non-veg food, night travel...",
)
pace = st.selectbox("Preferred pace", ["Relaxed", "Balanced", "Packed"])

if st.button("Draft my itinerary"):
    if not destination or not interests:
        st.warning("Add a destination and at least one interest.")
    elif not os.getenv("GROQ_API_KEY") or not os.getenv("LLM_MODEL"):
        st.error("Set GROQ_API_KEY and LLM_MODEL in your .env file.")
    else:
        client = OpenAI(
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=os.environ["GROQ_API_KEY"],
        )

        avoid_text = must_avoid.strip()
        if avoid_text:
            avoid_block = f"""
        Must avoid (hard constraints): {avoid_text}
        Do not suggest anything that conflicts with these. If a popular attraction
        in {destination} conflicts with them, leave it out and briefly say why.
        If the constraints involve food or health, tell the traveller to verify
        details directly with the venue rather than relying on this draft.
        """
        else:
            avoid_block = ""

        prompt = f"""
        Create a practical {days}-day draft itinerary for {destination}.
        Budget: {budget}
        Interests: {interests}
        Preferred pace: {pace}
        {avoid_block}
        Organize it by day. Suggest a few activities and include breaks.
        Do not claim that opening hours, prices, or transport details are current.
        Clearly mark anything the traveller should verify.
        """

        with st.spinner("Drafting your itinerary..."):
            try:
                result = client.chat.completions.create(
                    model=os.environ["LLM_MODEL"],
                    messages=[{"role": "user", "content": prompt}],
                )
            except Exception as e:
                st.error(f"Couldn't draft the itinerary: {e}")
                st.stop()

        st.markdown(result.choices[0].message.content)