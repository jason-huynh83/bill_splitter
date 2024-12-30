import streamlit as st
import pandas as pd
import base64
import json
from utils import get_dataframe, calculate_individual_shares
    
def main():
    st.title("Bill Splitter Web App")

    # Tutorial Section
    with st.expander("Tutorial", expanded=True):
        st.write("""
        **Welcome to the Bill Splitter App!**

        **How to Use:**

        1. **Submit Photo of Receipt**: Take a clear picture of the receipt or upload a photo of the receipt.
        2. **Enter Names Column**: In the names column please add the names of people splitting (separated with a comma)
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

    if uploaded_receipt is not None:
        image_bytes = uploaded_receipt.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        if 'df_image' not in st.session_state:
            with st.spinner("Reading Receipt . . ."):
                
                st.session_state.df_image = get_dataframe(base64_image)
      
            st.session_state.df_image['names'] = ''
        
        df_i = st.data_editor(st.session_state.df_image, num_rows = 'dynamic', use_container_width=True)
        
        df_i['price'] = df_i['price'].astype(float)
        df_i['names'] = df_i['names'].astype(str)
        
        
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
            shares = calculate_individual_shares(df_i, tax_percent, tip_percent, None, True)
            
        if option_selected == options[1]:
            tax_amount = tax_percent
            tip_amount = tip_percent
            grand_total = subtotal + tax_amount + tip_amount
            shares = calculate_individual_shares(df_i, tax_percent, tip_percent, subtotal, False)
            
        st.write('***************************')
        st.write(f"**Subtotal:** ${subtotal:,.2f}")
        st.write(f"**Tax:** ${tax_amount:,.2f}")
        st.write(f"**Tip:** ${tip_amount:,.2f}")
        st.write(f"**Grand Total:** ${grand_total:,.2f}")
        
        st.write('***************************')
        st.write("**Amount Each Person Owes:**")
        for person, amount in shares.items():
            st.write(f"{person}: ${amount:,.2f}")
        

if __name__ == "__main__":
    main()
    
# python -m streamlit run app.py