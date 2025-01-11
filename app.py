import streamlit as st
import pandas as pd
import base64
import json
from utils import get_dataframe, calculate_individual_shares, generate_detail_breakdown
from src.exception import CustomException
import sys
    
def main():
    st.title("Bill Splitter Web App")

    # Tutorial Section
    with st.expander("Tutorial", expanded=True):
        st.write("""
        **Welcome to the Bill Splitter App!**

        **How to Use:**

        1. **Submit Photo of Receipt**: Take a clear picture of the receipt or upload a photo of the receipt.
        2. **Enter Names**: Please add the names of people splitting the bill (separated with a comma), in the table below, toggle names for splitting
        3. **Ensure Table Matches Receipt**: In case of any discrepancies, the table is editable to make changes.
        4. **Review and Remove**:
           - View the list of dishes and their costs.
           - Add/Remove rows as needed
        5. **Calculate Costs**:
           - **Enter Tax and Tip Percentages**: Provide tax and tip percentages.
        **Note**: Each dish's cost is divided only among the people specified for that dish, so the final amount each person owes will reflect their share of the total costs.
        """)

    st.subheader("Step 1: Import Receipt")
    uploaded_receipt = st.file_uploader("Import image of Receipt")

    try:
        if uploaded_receipt is not None:
            image_bytes = uploaded_receipt.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            if 'df_image' not in st.session_state:
                with st.spinner("Reading Receipt . . ."):
                    
                    st.session_state.df_image = get_dataframe(base64_image)

            
                # st.session_state.df_image['names'] = ''
            st.subheader('Step 2: Enter names of all people splitting')
            names_input = st.text_input('Enter names (comma separated)', placeholder='e.g. Sam, Kobe, Jordan')
            
            names = [name.strip() for name in names_input.split(',') if name.strip()]
            
            if names:
                for name in names:
                    if name not in st.session_state.df_image.columns:
                        st.session_state.df_image['Everyone'] = False
                        st.session_state.df_image[name] = False
            
            df_i = st.data_editor(st.session_state.df_image, 
                                num_rows = 'dynamic', 
                                column_config={
                                    "names": st.column_config.CheckboxColumn(
                                        "Is this person splitting?",
                                        default = False
                                    )
                                },
                                use_container_width=True)
            
            
            df_i['price'] = df_i['price'].astype(float)
            
            subtotal = df_i['price'].replace('', 0).astype(float).sum()
            
            options = ['Percentage (%)', 'Dollar Value ($)']
            option_selected = st.pills("Tax and Tip By:", options, selection_mode = 'single', default=options[0])
            
            col1, col2 = st.columns(2)   
            
            with col1:
                tax_percent = st.number_input(f"Enter Tax {option_selected}", min_value=0.0, step=0.01)
            
            with col2:
                tip_percent = st.number_input(f"Enter Tip {option_selected}", min_value=0.0, step=0.01)

            if option_selected == options[0]:
                tax_amount = (tax_percent / 100) * subtotal
                taxed_subtotal = tax_amount + subtotal
                tip_amount = (tip_percent / 100) * taxed_subtotal
                grand_total = subtotal + tax_amount + tip_amount
                shares = calculate_individual_shares(df_i, tax_percent, tip_percent, subtotal, True)
                if not df_i.iloc[:, 3:].empty and df_i.iloc[:, 3:].any().any():
                    text_content = generate_detail_breakdown(df_i)
                    
                
            if option_selected == options[1]:
                tax_amount = tax_percent
                tip_amount = tip_percent
                grand_total = subtotal + tax_amount + tip_amount
                shares = calculate_individual_shares(df_i, tax_percent, tip_percent, subtotal, False)
                if not df_i.iloc[:, 3:].empty and df_i.iloc[:, 3:].any().any():
                    text_content = generate_detail_breakdown(df_i)

            
            st.write('***************************')
            st.write(f"**Subtotal:** ${subtotal:,.2f}")
            st.write(f"**Tax:** ${tax_amount:,.2f}")
            st.write(f"**Tip:** ${tip_amount:,.2f}")
            st.write(f"**Grand Total:** ${grand_total:,.2f}")
            
            st.write('***************************')
            st.write("**Amount Each Person Owes:**")
            
            for person, amount in shares.items():
                st.write(f"{person}: ${amount:,.2f}")
            
    except Exception as e:
        st.error('Error: Please enter Names of people')
        
    try:
        if uploaded_receipt is not None and len(names_input) > 0:
            if text_content:
                first_key = next(iter(text_content))  # Get the first key
                text_content.pop(first_key)

            
            detailed_breakdown = ''
                        
            for person, details in text_content.items():
                person_info = f"\n{person}:\n"
                detailed_breakdown += person_info
                
                for item, price in zip(details['Items'], details['Prices']):
                    price_info = f"    - {item}: ${round(price, 2)}\n"
                    detailed_breakdown += price_info

                tax_tip_info = f"Taxes and Tips: ${round(shares[person] - details['Total'], 2)}\n"
                detailed_breakdown += tax_tip_info 
                
                total_cost_info = f"Total Cost: ${round(shares[person], 2)}\n"
                detailed_breakdown += total_cost_info
        
            st.download_button(label = "Download Detailed Breakdown",
                            data = detailed_breakdown,
                            file_name = 'detailed_breakdown.txt')
    except:
        st.error('Please select names to split')

if __name__ == "__main__":
    main()
    
# python -m streamlit run app.py