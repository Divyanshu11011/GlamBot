import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import os
import requests
import io
from PIL import Image
import webcolors
import fal_client

# Load environment variables
load_dotenv()

# Set the FAL AI API key environment variable
os.environ['FAL_KEY'] = st.secrets["fal_ai"]["api_key"]

st.set_page_config(
    page_title="अtithi-Bots",
)

# Define the sidebar
with st.sidebar:
    # Create the options menu
    selected = option_menu(menu_title="अtithi",
                           options=["अtithi's GlamGuide"],
                           icons=["image"],
                           menu_icon="boxes",
                           default_index=0
                           )

def hex_to_name(hex_color):
    try:
        return webcolors.hex_to_name(hex_color)
    except ValueError:
        # If the exact name is not found, find the closest match
        min_colors = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - int(hex_color[1:3], 16)) ** 2
            gd = (g_c - int(hex_color[3:5], 16)) ** 2
            bd = (b_c - int(hex_color[5:7], 16)) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

def generate_prompt(selected_options, day, color_theme):
    gender = selected_options["gender"]
    bodyType = selected_options["bodyType"]
    complexion = selected_options["complexion"]
    weather = selected_options["weather"]
    eventType = selected_options["eventType"]
    region = selected_options["region"]
    color = hex_to_name(color_theme[day - 1]) if len(color_theme) > 1 else hex_to_name(color_theme[0])
    return f"Generate an image of a {gender} with {bodyType} body type, {complexion} complexion, wearing a dress to attend {eventType} in {weather} weather from {region}, with attire mainly composed of {color} color"

if selected == "अtithi's GlamGuide":
    st.title("Event-Related Clothing Suggestor")
    st.markdown("<p style='text-align:center;'>You can download the image with right click > save image</p>", unsafe_allow_html=True)

    options = {
        "gender": ["male", "female"],
        "bodyType": ["slim", "obese", "athletic"],
        "complexion": ["fair", "dusty", "dark"],
        "weather": ["sunny", "rainy", "cold"],
        "eventType": ["wedding", "birthday", "anniversary", "corporate event", "casual outing"],
        "region": ["South Asian", "African", "American", "Middle East"]
    }

    selected_options = {
        "gender": st.selectbox("Gender", options["gender"]),
        "bodyType": st.selectbox("Body Type", options["bodyType"]),
        "complexion": st.selectbox("Complexion", options["complexion"]),
        "weather": st.selectbox("Weather", options["weather"]),
        "eventType": st.selectbox("Event Type", options["eventType"]),
        "region": st.selectbox("Region", options["region"])
    }

    num_days = st.selectbox("Number of Event Days", [1, 2, 3, 4, 5])

    if num_days > 1:
        color_theme_choice = st.selectbox("Color Theme", ["Same for all days", "Different for each day"])
    else:
        color_theme_choice = "Same for all days"

    color_theme = []
    if color_theme_choice == "Same for all days":
        color = st.color_picker("Pick a Color")
        color_theme = [color] * num_days
    else:
        for i in range(num_days):
            color = st.color_picker(f"Pick a Color for Day {i+1}")
            color_theme.append(color)

    if st.button("Get Suggestions"):
        try:
            for day in range(1, num_days + 1):
                prompt = generate_prompt(selected_options, day, color_theme)

                handler = fal_client.submit(
                    "fal-ai/fast-lightning-sdxl",
                    arguments={
                        "model_name": "stabilityai/stable-diffusion-xl-base-1.0",
                        "prompt": prompt
                    }
                )

                result = handler.get()

                if result and "images" in result and len(result["images"]) > 0:
                    image_url = result["images"][0]["url"]
                    response = requests.get(image_url)
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption=f"Day {day}: {prompt}", use_column_width=True)
                else:
                    st.error(f"Failed to generate image for day {day}.")
        except Exception as e:
            st.error(f"Error generating images: {e}")
