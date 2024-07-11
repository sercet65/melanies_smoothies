# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write(
    """Choose your favorite fruits to make your custom Smoothie!
    """)


name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be :', name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Chose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
)
if ingredients_list:
    
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
        fv.df=st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
     
    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
    	
        st.success('Your Smoothie is ordered!', icon="✅")
        

fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
fv.df=st.dataframe(data=fruityvice_response.json(), use_container_width=True)


