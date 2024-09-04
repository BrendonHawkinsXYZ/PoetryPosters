import openai
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import requests
from io import BytesIO

# Set your OpenAI API key here
openai.api_key = "yours here"

# Function to generate a random subject or tone using GPT-4
def generate_random_variable(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.9,
        messages=[
            {"role": "system", "content": "you are a poet."},
            {"role": "user", "content": prompt}
        ]
    )
    variable = response['choices'][0]['message']['content'].strip()
    return variable

# Function to generate the haiku or poem using GPT-4
def generate_poem(main_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.9,
        messages=[
            {"role": "system", "content": "You are a poet."},
            {"role": "user", "content": main_prompt}
        ]
    )
    poem = response['choices'][0]['message']['content'].strip()
    return poem

# Step 2: Break Down the Poem into words
def break_down_poem(poem):
    words = poem.split()
    return words

def fetch_random_unsplash_image(access_key):
    url = "https://api.unsplash.com/photos/random"
    params = {"orientation": "portrait"} 
    headers = {"Authorization": f"Client-ID {access_key}"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        image_url = response.json()['urls']['regular']
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        return img
    else:
        print("Error: Unable to fetch image from Unsplash. Status code:", response.status_code)
        return None

# Function to scale the image to the canvas size
def scale_image_to_canvas(image, canvas_width, canvas_height):
    return image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)

#Function to blur the image
def apply_blur(image, blur_radius=50):
    return image.filter(ImageFilter.GaussianBlur(blur_radius))

# Function to create the poster
def create_poster(words, width=3900, height=5700, padding=100, background_image=None):
    # Select a random style
    style = random.choice([1, 2, 3, 4, 5])
    
    # Determine background and text settings based on style
    if style == 1:
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        text_colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in words]
    elif style == 2:
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        text_colors = [(0, 0, 0) for _ in words]
    elif style == 3:
        if background_image:
            # Apply blur to the background image
            blurred_image = apply_blur(background_image, blur_radius=15)
            img = scale_image_to_canvas(blurred_image, width, height)
        else:
            img = Image.new('RGB', (width, height), color=(0, 0, 0))
        text_colors = [(0, 0, 0)]
    elif style == 4:
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        text_colors = [(255, 255, 255) for _ in words]
    elif style == 5:
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        text_colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in words]

    draw = ImageDraw.Draw(img)


    draw = ImageDraw.Draw(img)
    
    fonts = ['Strasua.otf', 'SF-Pro-Text-Light.otf', 'fast_money.ttf', 'BM_Pixel.otf', 'Baby Aletha.otf']
    sizes = [300, 350, 200, 150]

    cursor_x = padding
    cursor_y = padding
    
    max_width = width - 2 * padding
    
    for i, word in enumerate(words):
        font_name = random.choice(fonts)
        font_size = random.choice(sizes)
        font = ImageFont.truetype(font_name, font_size)
        
        word_color = text_colors[i % len(text_colors)]

        bbox = draw.textbbox((0, 0), word, font=font)
        word_width = bbox[2] - bbox[0]
        word_height = bbox[3] - bbox[1]

        if cursor_x + word_width > max_width and style != 5:
            cursor_x = padding
            cursor_y += word_height + 50

        if cursor_y + word_height > height - padding and style != 5:
            break

        if style == 5:
            x = random.randint(0, width - word_width)
            y = random.randint(0, height - word_height)
            angle = random.randint(0, 360)
            word_img = Image.new('RGBA', (word_width, word_height), (255, 255, 255, 0))
            word_draw = ImageDraw.Draw(word_img)
            word_draw.text((0, 0), word, font=font, fill=word_color)
            word_img = word_img.rotate(angle, expand=1)
            img.paste(word_img, (x, y), word_img)
        else:
            draw.text((cursor_x, cursor_y), word, font=font, fill=word_color)
            cursor_x += word_width + 10
    
    return img

# Function to save the poster
def save_poster(img, base_filename='poster'):
    filename = f"{base_filename}.png"
    i = 1
    while os.path.exists(filename):
        filename = f"{base_filename}_{i}.png"
        i += 1
    img.save(filename)
    print(f"Poster saved as {filename}")

# Main function
def main():
    # Your Unsplash API access key
    unsplash_access_key = "yours here"

    # Fetch a random nature image from Unsplash
    background_image = fetch_random_unsplash_image(unsplash_access_key)

    subject_prompt = "Give me a random abstract subject to write a poem about."
    tone_prompt = "Give me a random literary style or tone to write a poem in."

    variable1 = generate_random_variable(subject_prompt)
    variable2 = generate_random_variable(tone_prompt)

    main_prompt = f"Write a poem about {variable1} in the tone of {variable2}."
    
    print("Generated Main Prompt:")
    print(main_prompt)

    poem = generate_poem(main_prompt)

    print("Generated Poem:")
    print(poem)

    words = break_down_poem(poem)

    poster = create_poster(words, background_image=background_image)
    save_poster(poster)

if __name__ == "__main__":
    main()
