#!/usr/bin/env python
# coding: utf-8

# In[7]:


import altair as alt
import pandas as pd
from vega_datasets import data

choco = pd.read_csv('./flavors_of_cacao.csv')


# In[8]:


# rename the columns
original_colnames = choco.columns
new_colnames = ['company', 'species', 'REF', 'review_year', 'cocoa_p',
                'company_location', 'rating', 'bean_typ', 'country']
choco = choco.rename(columns=dict(zip(original_colnames, new_colnames)))
## And modify data types
choco['cocoa_p'] = choco['cocoa_p'].str.replace('%','').astype(float)/100
choco["species"] = choco["species"].str.split(",").str[0]


# ## LO1: The user will recognize important cocoa production areas worldwide
# This visualization aims at presenting the important cocoa production country worldwide. It uses the data of chocolate bars production, selects the species of cocoa beans and their origin country, and use it as the country of origin for cocoa production. It is plotted in format of a choropleth map on a world map, where deeper color represents greater cocoa production. It presents the geographical distribution of cocoa prodcution in a intuitive way, as deep color and large, connected area will give user an impression that the area on map is significant in cocoa production. The color scheme is selected so that it fits the impression of cocoa and chocolate. This learning objective can be evaluated by testing users how they recognize the geographical distribution of cocoa production areas.

# In[9]:


# a simplified data frame of country of origin of cocoa
species = pd.DataFrame(choco['species'].value_counts().reset_index())
species.columns=['name', 'count']
species['id']=range(0, len(species))


# Following is an alternative visualization of the map plot. It shows the country name and its production more precisely, but not as intuitive as the map plot.

# In[10]:


cocoa = pd.read_csv('./Flavors_of_Cacao2022.csv')


# In[11]:


import pycountry

def lookup(name):
    try:
        return pycountry.countries.lookup(name).numeric
    except LookupError:
        return None


cocoa_species = pd.DataFrame(cocoa['Country of Bean Origin'].value_counts().reset_index())
cocoa_species = cocoa_species.replace('U.S.A.', 'USA')
cocoa_species.columns=['name', 'count']
cocoa_species['id']=range(0, len(cocoa_species))
cocoa_species['uid']=cocoa_species['name'].apply(lambda name : lookup(name))


# In[12]:


country = alt.topo_feature(data.world_110m.url, 'countries')
brush = alt.selection_interval(encodings=['y'])
opacityCond = alt.condition(brush,alt.value(1),alt.value(0.6))
colorCond = alt.condition(brush,alt.value(1),alt.value(0.6))
color2 = alt.Chart(country).mark_geoshape().encode(
    #color=alt.Color('count:Q', scale=alt.Scale(scheme="browns"), legend=None,),
    color = alt.condition(brush,
                      alt.Color('count:Q', scale=alt.Scale(scheme="browns"), legend=None),
                      alt.value('linen')),
    tooltip=[
            alt.Tooltip("name:N", title="Country"),
            alt.Tooltip("count:Q", title="Count"),
        ],
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(cocoa_species, 'uid', list(cocoa_species.columns))
).project("naturalEarth1").properties(width=600, height=400)
background2 = alt.Chart(country).mark_geoshape(fill="linen").project("naturalEarth1").properties(width=600, height=400)


bars = alt.Chart(cocoa_species).mark_bar().add_selection(brush).encode(
    y=alt.Y('name:N',sort=alt.EncodingSortField(
            field="count",order="descending"), title="Country of origin of cocoa"),
    x=alt.X('count:Q'),
    color=alt.Color("count:Q", scale=alt.Scale(scheme="browns")),
    opacity=opacityCond, 
).transform_window(
    rank='rank(count)',
    sort=[alt.SortField('count', order='descending')]
).transform_filter(
    (alt.datum.rank < 30)
).properties(width=200, height=400)
background2+color2 | bars


# ## LO2: The user will summarize the preferance of chocolate consumption by country
# This visualization aims at presenting the preferance of chocolate type by cocoa percent, grouped by country. It uses count of chocolate bar production to represents the preference, grouped by country and cocoa percent. As this visualization is targeted at informing user the preferance between chocolate types, and how the preferance varies between country, the final result is normalized to percentage of total production. The color of stacked bars implicitly indicates the type of chocolate, makes the visualization more intuitive. This learning objective can be evaluated by asking users what type of chocolate is favored by each country.

# In[13]:


countries2 = pd.DataFrame(choco['company_location'].value_counts().reset_index())
countries2.columns=['name', 'count']
countries2 = countries2[countries2['count'] >= 40]


# Following is an old version of this visualization. It uses scatter points to show the production of each type of chocolate by country, and its production amount. It can be seen that USA has much larger production than other countries, but I think comparation between chocolate types is more emphasized in this visualization than production amount, so I normalized it and changed to a bar chart.

# In[16]:


country_options = countries2['name'].tolist()
selections2 = alt.binding_select(options=country_options, name="Show: ")
buttons2 = alt.selection_single(fields=['company_location'], bind=selections2, 
                                init={'company_location': "U.S.A."},)
vis2 = alt.Chart(choco).mark_bar().transform_filter(
        buttons2
    ).encode(
        x=alt.X("cocoa_p:Q", bin=True,title="Cocoa percent"),
        y=alt.Y("count(cocoa_p):Q", title="Count"),
        color=alt.Color("cocoa_p:Q", bin=True, 
                        scale=alt.Scale(scheme=alt.SchemeParams(name="browns", extent=[0, 2])), 
                        title="Cocoa percent"),
    ).properties(width=600)
vis2.add_selection(buttons2)


# ## LO3: The user will be able to infer the effect of chocolate on health
# This visualization will compare the health data of 45 participants that accepts a clinical trial over a duration of four weeks. The participants are given 70% cocoa chocolate with acids (ursolic acids and oleanolic acid) from a Brazilian plant, Mansoa Hirsuta,and the goal of the test was to determine whether Mansoa Hirsuta's antioxidant, anti-inflammatory, antifungal, and antibiotic properties improve health.
# The visualization is in format of bar chart, grouped by health parameters and put the before-after bars side to side, so that the change before and after the clinical trial can be identified clearly, and the effect of chocolate on health can be inferred based on the observation. This learning objective can be evaluated by asking users whether there is evidence that chocolate has an effect on health.

# In[17]:


filepath = './BMI weight and waist circumference of participants.csv'
health = pd.read_csv(filepath)


# In[18]:



options3 = ["Weight (kg)", "BMI (kg/m^2)", "Waist Circumference (cm)"]
buttons3 = alt.selection_single(
    fields=["variable"],
    bind=alt.binding_radio(options=options3, labels=["Weight", "BMI", "Waist Circumference"], name="Parameter: "),)
vis3 = alt.Chart(health).mark_bar().transform_filter(
    buttons3
).encode(
    x=alt.X("trial:N", title=None),
    y=alt.Y("mean:Q"),
    color=alt.Color("group:N"),
    #column=alt.Column("trial", sort=["Before", "After"]),
    #column=alt.Column("variable", sort=["Weight (kg)", "BMI (kg/m^2)", "Waist Circumference (cm)"])
    column=alt.Column("group", sort=["Test", "Placebo", "Control"], title="Waist Circumference (cm)")
)
vis3.add_selection(buttons3)


# ## LO4: The user will summary the nutrition facts of chocolate
# This visualization uses the data of nutrient facts of chocolate bars produced by different manufactors, and use a boxplot to present the calories and fat contained every 100 grams. A boxplot presents maximum, minimum, average and quaters value, gives users a summary of nutrient facts of chocolates. This learning objective can be evaluated by how much energy they would intake if they eat a bar of chocolate.

# In[19]:


nutrient = pd.read_csv("chocolates.csv")


# There are also scatter points version of this visualization, which enables users to see what brand of chocolate has most and least calories. Since it is not very related to contents of wikipedia article, it is not used in the article.

# In[20]:


types = nutrient["Type"].drop_duplicates().tolist()
selection4 = alt.binding_select(options=types, name="Chocolate type: ")
buttons4 = alt.selection_single(fields=['Type'], bind=selection4, )
milk_points = alt.Chart(nutrient).transform_filter(
    buttons4
).mark_point(opacity=0.5).encode(
    x=alt.X("MFR:N"),
    y=alt.Y("Calories:Q", scale=alt.Scale(domain=[200, 800])),
    color="Type",
    tooltip=['Name','MFR','Country','Calories']
).properties(width=600)
# milk_texts = alt.Chart(nutrient).transform_filter(
#     (alt.datum.Type == "Milk") & ((alt.datum.Calories > 600) | (alt.datum.Calories < 490))
# ).mark_text(dy=-10).encode(
#     x=alt.X("MFR:N"),
#     y=alt.Y("Calories:Q"),
#     text=alt.Text("Name")
# )
milk_points.add_selection(buttons4)


# ## Datasets source:
#  1. Chocolate Bar Ratings. https://www.kaggle.com/datasets/rtatman/chocolate-bar-ratings
#  2. Cocoa chocolate and health. https://www.kaggle.com/datasets/lameesmohammad/unique-70-cocoa-chocolate-improves-health
#  3. chocolates.csv. https://github.com/schloerke/cranvasOLD/blob/master/files/data/chocolates.csv

# In[ ]:
import streamlit as st

countries = alt.topo_feature(data.world_110m.url, 'countries')
# The world image
world_map = alt.Chart(countries).mark_geoshape(
    fill='#EEEEEE',
    stroke='white'
)
# The export image
# hover在上面会出现这个国家具体出口量是多少
# hover在上面会出现这个国家具体排名
map_chart_export = alt.Chart(df_map).mark_geoshape().transform_filter(
    alt.datum.Export == 'E'
).transform_window(
    sort=[alt.SortField('Value2021', order='descending')],
    rank='rank()'
).encode(
    color=alt.Color('Value2021:Q', scale=alt.Scale(
        scheme='blues'), title='Main Export Countries'),
    tooltip=[alt.Tooltip('Value2021:Q', title='Export amount'), 'rank:Q']
).transform_lookup(
    lookup='Code',
    from_=alt.LookupData(countries, key='id', fields=[
                         "type", "properties", "geometry"])
)

# the import image
map_chart_import = alt.Chart(df_map).mark_geoshape().transform_filter(
    alt.datum.Export == 'I'
).transform_window(
    sort=[alt.SortField('Value2021', order='descending')],
    rank='rank()'
).encode(
    color=alt.Color('Value2021:Q', scale=alt.Scale(
        scheme='reds'), title='Main Import Countries'),
    tooltip=[alt.Tooltip('Value2021:Q', title='Import amount'), 'rank:Q']
).transform_lookup(
    lookup='Code',
    from_=alt.LookupData(countries, key='id', fields=[
                         "type", "properties", "geometry"])
)

Chart1 = (world_map+(map_chart_export+map_chart_import).resolve_scale(color='independent')).configure(
    background='transparent'
).project(
    'mercator'
).properties(
    width=800,
    height=600,
    title='Distribution of Top Import and Export Countries of Acai'
).configure_title(fontSize=24)

st.altair_chart(Chart1)


# In[ ]:




