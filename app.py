import streamlit as st
import pandas as pd

# Initialize session state variables
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Dish Name', 'Dish Price', 'Num People Splitting'])

# Function to remove a row by index
def remove_row(index):
    st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)

# Function to calculate individual shares
def calculate_individual_shares(df, tax_amount, tip_amount):
    shares = {}
    for _, row in df.iterrows():
        dish_price = row['Dish Price'] * (1 + (tax_amount/100)) * (1 + (tip_amount/100))
        num_people_splitting = row['Num People Splitting']
        names = [row[f'Name {i+1}'] for i in range(num_people_splitting) if pd.notna(row[f'Name {i+1}'])]

        if len(names) > 0:
            amount_per_person = dish_price / len(names)
            for name in names:
                shares[name] = shares.get(name, 0) + amount_per_person
    return shares

def main():
    st.title("Bill Splitter Web App")
    
    # Tutorial Section
    with st.expander("Tutorial", expanded=True):
        st.write("""
        **Welcome to the Bill Splitter App!**

        **How to Use:**

        1. **Enter the Number of People**: Specify how many people are splitting the bill.

        2. **Add Dishes**:
           - **Dish Name**: Enter the name of the dish.
           - **Dish Price**: Enter the price of the dish.
           - **Number of People to Split**: Select how many people will split the cost of this dish.
           - **Names to Split Dish**: Enter the names of the people splitting this dish (comma-separated).

        3. **Submit**: Click the "Submit" button to add the dish and its cost details to the list.

        4. **Review and Remove**:
           - View the list of dishes and their costs.
           - Use the dropdown to select a row to remove if needed.

        5. **Calculate Costs**:
           - **Enter Tax and Tip Percentages**: Provide tax and tip percentages.
           - **View Individual Shares**: See how much each person owes based on the dishes they ordered.

        **Note**: Each dish's cost is divided only among the people specified for that dish, so the final amount each person owes will reflect their share of the total costs.
        """)

    # Input the number of people splitting the bill
    num_people = st.number_input("Enter the number of people splitting the whole bill:", min_value=1, step=1)
    
    # Create a form for dish details
    with st.form(key='dish_details_form'):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            dish_name = st.text_input("Enter Dish Name:")
            
        with col2:
            dish_price = st.number_input("Enter Dish Price:", min_value=0.0, step=0.01)
        
        with col3:
            num_ppl_splitting_dish = st.selectbox("Number of people to split:", options=range(1, num_people + 1))
        
        with col4:
            names_to_split = st.text_input("Name(s), use comma:", placeholder="Jason, Celia")
        
        submit_button = st.form_submit_button(label='Submit')
    
    # Add dish details to DataFrame when the form is submitted
    if submit_button:
        names_list = [name.strip() for name in names_to_split.split(',')]

        new_row = {
            'Dish Name': dish_name,
            'Dish Price': dish_price,
            'Num People Splitting': num_ppl_splitting_dish,
        }

        for idx, name in enumerate(names_list):
            new_row[f'Name {idx+1}'] = name

        new_df = pd.DataFrame([new_row])

        existing_columns = st.session_state.df.columns
        for col in new_df.columns:
            if col not in existing_columns:
                st.session_state.df[col] = pd.NA

        st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
    
    # Display the DataFrame with enhanced styling
    if not st.session_state.df.empty:
        st.write("Current Entries:")
        df_no_nan = st.session_state.df.fillna('')
        
        styled_df = df_no_nan.style.format({
            'Dish Price': '${:,.2f}',
            'Num People Splitting': '{:.0f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
        
        subtotal = st.session_state.df['Dish Price'].replace('', 0).astype(float).sum()
        
        # Dropdown to select which row to remove
        row_to_remove = st.selectbox(
            "Mistake? Select a row to remove:", 
            options=st.session_state.df.index.tolist(), 
            format_func=lambda x: f"Row {x} - {st.session_state.df.at[x, 'Dish Name']}"
        )

        # Remove button to delete the selected row
        if st.button("Remove Selected Row"):
            if row_to_remove is not None:
                remove_row(row_to_remove)
                st.experimental_rerun()  # Use experimental_rerun to refresh without needing manual intervention
                
        st.write('***************************')
        col1, col2 = st.columns(2)
        
        with col1:
            tax_percent = st.number_input("Enter Tax (%)", min_value=0.0, step=0.01)
        
        with col2:
            tip_percent = st.number_input("Enter Tip (%)", min_value=0.0, step=0.01)

        tax_amount = (tax_percent / 100) * subtotal
        taxed_subtotal = tax_amount + subtotal
        tip_amount = (tip_percent / 100) * taxed_subtotal
        grand_total = subtotal + tax_amount + tip_amount

        if num_people > 0:
            shares = calculate_individual_shares(st.session_state.df, tax_percent, tip_percent)
            st.write("**Amount Each Person Owes:**")
            for person, amount in shares.items():
                st.write(f"{person}: ${amount:,.2f}")
        
        st.write('***************************')
        st.write(f"**Subtotal:** ${subtotal:,.2f}")
        st.write(f"**Tax:** ${tax_amount:,.2f}")
        st.write(f"**Tip:** ${tip_amount:,.2f}")
        st.write(f"**Grand Total:** ${grand_total:,.2f}")

if __name__ == "__main__":
    main()