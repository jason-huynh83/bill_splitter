from openai import OpenAI
import yaml
import os
import pandas as pd
import json 
import streamlit as st


def get_dataframe(base64_image):
    # with open("config.yaml", "r") as file:
    #     config = yaml.safe_load(file)

    # os.environ["OPENAI_API_KEY"] = config["token"]

    client = OpenAI(
        # api_key=os.environ.get("OPENAI_API_KEY")
        api_key=st.secrets['OPENAI_API_KEY']
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """You are being shown receipts from a restaurant. Please correctly parse out all items, quantity and prices in the following receipt shown. 
                    After parsing the data, You will return the extracted information in a JSON object, using the following schema:
                        {
                        "Quantity": (float),
                        "Item": (string),
                        "price": (float)
                        }
                    Do not include markdown formatting in your response. Do not include any explanatory notes. Do not include newline character, dollar or other symbols, stick to strings and numerical notation. Make sure the JSON object is valid"""},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )
    parsed_data = response.choices[0].message.content

    # Assuming parsed_data is a string representation of JSON, convert it to a Python object
    try:
        # Convert the string to a list of dictionaries
        item_list = json.loads(parsed_data)  # Use json.loads to parse the string
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        item_list = []

    # Create a DataFrame from the list of dictionaries
    if item_list:  # Check if item_list is not empty
        df = pd.DataFrame(item_list)
        return df
    else:
        print("No valid data to create a DataFrame.")


def calculate_individual_shares(df, tax_amount, tip_amount, subtotal, is_percentage):
    
    shares = {}
    for _, row in df.iterrows():
        
        if is_percentage:
            dish_price = row['price'] * (1 + (tax_amount / 100)) * (1 + (tip_amount / 100))
        else:
            proportion = row['price'] / subtotal
            tax_share = tax_amount * proportion
            tip_share = tip_amount * proportion
            dish_price = row['price'] + tax_share + tip_share
        
        
        # Checks if "Everyone" exists and if value == True
        if row.get("Everyone", False):
            # If exists and is True, then get all names outside specified cols
            names = [col.strip() for col in df.columns if col not in ['Quantity','Item','price','Everyone']]
            
        else:
            # If not in row or is False, then get columns outside specified rows
            names = [col.strip() for col in df.columns if row[col] is True and col not in ['Quantity','Item','price','Everyone']]
        
        num_people_splitting = len(names)
        
        for name in names:
            if name in shares:
                shares[name] += dish_price / num_people_splitting
            else:
                shares[name] = dish_price / num_people_splitting
                
    return shares