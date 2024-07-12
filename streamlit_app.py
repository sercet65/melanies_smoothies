import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd
from snowflake.snowpark.exceptions import SnowparkSQLException

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write(
    """Choose your favorite fruits to make your custom Smoothie!
    """)

# Input for name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be :', name_on_order)

# Establish connection to Snowflake
try:
    cnx = st.experimental_connection("snowflake")
    session = cnx.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()
except SnowparkSQLException as e:
    st.error("Failed to fetch data from Snowflake: " + str(e))
    st.stop()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Display nutrition information for each selected fruit
    for fruit_chosen in ingredients_list:
        search_on = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        
        st.subheader(f'{fruit_chosen} Nutrition Information')
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            if fruityvice_response.status_code == 200:
                nutrition_info = fruityvice_response.json()
                st.json(nutrition_info)
            else:
                st.write("Nutrition information not available.")
        except Exception as e:
            st.error("Failed to fetch nutrition information: " + str(e))
    
    st.write('Ingredients:', ingredients_string)

    # SQL statement to insert the order into Snowflake
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    st.write(my_insert_stmt)

    # Button to submit the order
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except SnowparkSQLException as e:
            st.error("Failed to submit order: " + str(e))
