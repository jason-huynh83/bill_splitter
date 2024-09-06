import streamlit as st
import pandas as pd

# Initialize session state variables
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Dish Name', 'Dish Price', 'Num People Splitting'])

if 'all_names' not in st.session_state:
    st.session_state.all_names = []  # List to store all names

if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0  # Counter to trigger refresh

# Function to remove a row by index
def remove_row(index):
    st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
    st.session_state.refresh_counter += 1  # Increment counter to trigger UI refresh

# Function to calculate individual shares
def calculate_individual_shares(df, tax_amount, tip_amount):
    shares = {}
    for _, row in df.iterrows():
        dish_price = row['Dish Price'] * (1 + (tax_amount / 100)) * (1 + (tip_amount / 100))
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

        1. **Enter All Names**: Provide all names involved in splitting the bill.
        2. **Add Dishes**:
           - **Dish Name**: Enter the name of the dish.
           - **Dish Price**: Enter the price of the dish.
           - **Select Names to Split Dish**: Choose names from the list of people who will split the cost of this dish.
        3. **Submit**: Click the "Submit" button to add the dish and its cost details to the list.
        4. **Review and Remove**:
           - View the list of dishes and their costs.
           - Use the dropdown to select a row to remove if needed.
        5. **Calculate Costs**:
           - **Enter Tax and Tip Percentages**: Provide tax and tip percentages.
           - **View Individual Shares**: See how much each person owes based on the dishes they ordered.
        **Note**: Each dish's cost is divided only among the people specified for that dish, so the final amount each person owes will reflect their share of the total costs.
        """)

    # Input all names once at the start
    st.subheader("Step 1: Enter All Names")
    all_names = st.text_input("Enter names of all people splitting the bill (comma-separated):", placeholder="Jason, Celia, Tom")
    if st.button("Submit Names"):
        st.session_state.all_names = [name.strip() for name in all_names.split(',') if name.strip()]
    
    # Proceed only if names are submitted
    if st.session_state.all_names:
        st.write("People splitting the bill:", st.session_state.all_names)
        
        # Create a form for dish details
        st.subheader("Step 2: Add Dishes")
        with st.form(key='dish_details_form'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                dish_name = st.text_input("Enter Dish Name:")
                
            with col2:
                dish_price = st.number_input("Enter Dish Price:", min_value=0.0, step=0.01)
            
            with col3:
                # Add "All" option and handle selection
                options = ["All"] + st.session_state.all_names
                names_to_split = st.multiselect("Select people to split the dish:", options=options)
                
                # If "All" is selected, replace the selection with all names
                if "All" in names_to_split:
                    names_to_split = st.session_state.all_names
            
            submit_button = st.form_submit_button(label='Submit')
        
        # Add dish details to DataFrame when the form is submitted
        if submit_button and names_to_split:
            new_row = {
                'Dish Name': dish_name,
                'Dish Price': dish_price,
                'Num People Splitting': len(names_to_split),
            }

            # Add each selected name as a separate column dynamically
            for idx, name in enumerate(names_to_split):
                new_row[f'Name {idx+1}'] = name

            new_df = pd.DataFrame([new_row])

            # Ensure existing columns in st.session_state.df
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