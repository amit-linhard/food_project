import streamlit as st
import pandas as pd
import base64
from urllib.parse import urlparse
from pathlib import Path
from word2vec_rec import get_recs
from PIL import Image

def extract_recipe_name(url):
    parsed_url = urlparse(url)
    p = Path(parsed_url.path)
    return p.parts[-1].replace("-"," ")


def make_clickable(url):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = extract_recipe_name(url)
    return f'<a target="_blank" href="{url}">{text}</a>'

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo


def main():
    cs_sidebar()
    cs_body()

def cs_sidebar():
    st.sidebar.markdown("<h3 style='text-align: center; color: black;'>Filter By :</h1>", unsafe_allow_html=True)
    st.sidebar.selectbox("Cuisines",['All',"Chinese", "Italian", "Mexican", "French", "Indian", "Japanese", "Thai",  "American"])
    st.sidebar.selectbox("Cooking Time (Minutes)",['All','15','30','45','60','75','90','105','120'])
    st.sidebar.selectbox("Difficulty",['All','Easy','Medium','Hard'])
    # st.sidebar.markdown(":heart:")
    col_a, col_b, col_c = st.sidebar.columns((2, 4, 2))
    col_b.markdown("## Liked Recipes :heart:")
    # st.sidebar.markdown("<h1 style='text-align: center; color: black;'>Liked Recipes: </h1>", unsafe_allow_html=True)
    st.sidebar.code('''Your recipe box, your rules!
Browse through your saved and liked recipes,
and whip up a favorite again and again''')
    df = pd.read_csv('input\sample_user_saved_items.csv')[['recipe_urls','user_rank']]
    df['recipe_urls'] = df['recipe_urls'].apply(make_clickable)
    st.sidebar.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)


def cs_body():
    st.markdown("<h1 style='text-align: center; color: black;'>Meal Marvel</h1>", unsafe_allow_html=True)

    st.markdown("<h5 style='text-align: center; color: black;'>Culinary Genius </h5>", unsafe_allow_html=True)

    st.markdown(
        "## Insert your ingredients, and get suggestions for recipes you can cook! :falafel:"
    )

    if 'recipe_df' not in st.session_state:
        st.session_state['recipe_df'] = ""
    if 'recipes' not in st.session_state:
        st.session_state['recipes'] = ""
    if 'model_computed' not in st.session_state:
        st.session_state['model_computed'] = False
    if 'execute_recsys' not in st.session_state:
        st.session_state['execute_recsys'] = False
    if 'recipe_df_clean' not in st.session_state:
        st.session_state['recipe_df_clean'] = ""
    if 'five_recipes_to_show' not in st.session_state:
        st.session_state.five_recipes_to_show = ""


    ingredients = st.text_input(
        "Enter ingredients you would like to cook with (seperate ingredients with a comma)",
        "tomato, rice, cream cheese, beef"
    )

    st.session_state.execute_recsys = st.button("Give me recommendations!")
    if st.session_state.execute_recsys:
        # col1, col2, col3 = st.beta_columns([1, 6, 1])
        col1, col2, col3 = st.columns([4, 5, 4])
        with col2:
            gif_runner = st.image("input/drum chef.gif")
        # "recipie" holds 5 recommended recipes:
        recipe = get_recs(ingredients, mean=True)
        gif_runner.empty()
        st.session_state.recipe_df_clean = recipe.copy()
        # link is the column with hyperlinks
        # recipe["url"] = recipe.apply(
        #     lambda row: make_clickable(row["recipe"], row["url"]), axis=1
        # )
        recipe_display = recipe[
            ["recipe", "url", "ingredients", "cooking_time", "difficulty", "general rating", "liked?"]]
        st.session_state.five_recipes_to_show = recipe_display
        st.session_state.recipe_display = recipe_display.to_html(escape=False)
        st.session_state.recipes = recipe.recipe.values.tolist()
        st.session_state.model_computed = True
        st.session_state.execute_recsys = False

    if st.session_state.model_computed:
        # st.write("Either pick a particular recipe or see the top 5 recommendations.")
        recipe_all_box = st.selectbox(
            "It's up to you: Either see the top 5 recommendations or pick a particular recipe",
            ["Show top 5 recipes", "Select a single recipe"],
        )
        if recipe_all_box == "Show top 5 recipes":

            # st.write(st.session_state.recipe_display, unsafe_allow_html=True)
            col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8 = st.columns((2, 2, 2, 8, 3, 3, 2, 2))
            col_2.markdown("**:blue[recipe]**")
            col_3.markdown("**:blue[url]**")
            col_4.markdown("**:blue[ingredients]**")
            col_5.markdown("**:blue[cook time]**")
            col_6.markdown("**:blue[difficulty]**")
            col_7.markdown("**:blue[rank]**")
            col_8.markdown("**:blue[liked?]**")
            for x, like in enumerate(st.session_state.five_recipes_to_show['recipe']):
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns((1, 2, 2, 8, 2, 2, 1, 2))
                col1.write(x)  # index
                col2.write(st.session_state.five_recipes_to_show['recipe'][x])
                col3.write(st.session_state.five_recipes_to_show['url'][x])
                col4.write(st.session_state.five_recipes_to_show['ingredients'][x], use_column_width=True)  # email status
                col5.write(st.session_state.five_recipes_to_show['cooking_time'][x])
                col6.write(st.session_state.five_recipes_to_show['difficulty'][x])
                col7.write(st.session_state.five_recipes_to_show['general rating'][x])
                disable_status = st.session_state.five_recipes_to_show['liked?'][x]
                button_phold = col8.empty()
                do_action = button_phold.button("like", key=x)
        else:
            selection = st.selectbox(
                "Select a delicious recipe", options=st.session_state.recipes
            )
            selection_details = st.session_state.recipe_df_clean.loc[
                st.session_state.recipe_df_clean.recipe == selection
                ]
            st.markdown(f"# {selection_details.recipe.values[0]}")
            st.subheader(f"Website: {selection_details.url.values[0]}")
            ingredients_disp = selection_details.ingredients.values[0].split(",")

            st.subheader("Ingredients:")
            col1, col2 = st.columns(2)
            ingredients_disp = [
                ingred
                for ingred in ingredients_disp
                if ingred
                   not in [
                       " skin off",
                       " bone out",
                       " from sustainable sources",
                       " minced",
                   ]
            ]
            ingredients_disp1 = ingredients_disp[len(ingredients_disp) // 2:]
            ingredients_disp2 = ingredients_disp[: len(ingredients_disp) // 2]
            for ingred in ingredients_disp1:
                col1.markdown(f"* {ingred}")
            for ingred in ingredients_disp2:
                col2.markdown(f"* {ingred}")


if __name__ == '__main__':
    main()

