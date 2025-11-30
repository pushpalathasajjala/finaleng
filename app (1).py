
import streamlit as st
import pandas as pd
import altair as alt

file_path = '/content/forecast_results_2024_2029 (5) (1).xlsx'
df = pd.read_excel(file_path)

year_cols = [col for col in df.columns if col.startswith('pred_')]
id_vars = [col for col in df.columns if col not in year_cols]
df_melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name='Year', value_name='Forecast Value')
df_melted['Year'] = df_melted['Year'].str.replace('pred_', '').astype(int)

countries = sorted(df_melted['Area'].unique())
categories = sorted(df_melted['Category'].unique())
years = sorted(df_melted['Year'].unique())

st.set_page_config(layout="wide")
st.title('Forecast Results Dashboard')

st.sidebar.header('Filter Options')

selected_countries = st.sidebar.multiselect('Select Country', options=countries, default=countries)
selected_categories = st.sidebar.multiselect('Select Category', options=categories, default=categories)
selected_years = st.sidebar.multiselect('Select Year', options=years, default=years)

filtered_df = df_melted[
    (df_melted['Area'].isin(selected_countries)) &
    (df_melted['Category'].isin(selected_categories)) &
    (df_melted['Year'].isin(selected_years))
]

st.write(f"Filtered data shape: {filtered_df.shape[0]} rows, {filtered_df.shape[1]} columns.")

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
else:
    st.header('Interactive Graphs')

    chart1 = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X('Year:O', axis=alt.Axis(format='d')),
        y=alt.Y('Forecast Value:Q'),
        color='Category:N',
        tooltip=['Year', 'Category', 'Forecast Value', 'Area']
    ).properties(title='Forecast Value Over Years by Category').interactive()

    chart2_df = filtered_df.groupby('Category')['Forecast Value'].mean().reset_index()
    chart2 = alt.Chart(chart2_df).mark_bar().encode(
        x=alt.X('Category:N', sort='-y'),
        y=alt.Y('Forecast Value:Q', title='Average Forecast Value'),
        tooltip=['Category', 'Forecast Value']
    ).properties(title='Average Forecast Value per Category').interactive()

    chart3_df = filtered_df[['Model', 'MAE', 'RMSE']].drop_duplicates()
    chart3 = alt.Chart(chart3_df).mark_circle(size=60).encode(
        x=alt.X('MAE:Q'),
        y=alt.Y('RMSE:Q'),
        color='Model:N',
        tooltip=['Model', 'MAE', 'RMSE']
    ).properties(title='Model Performance: MAE vs RMSE').interactive()

    chart4_df = filtered_df.groupby(['Year', 'Country_Type'])['Forecast Value'].sum().reset_index()
    chart4 = alt.Chart(chart4_df).mark_area().encode(
        x=alt.X('Year:O', axis=alt.Axis(format='d')),
        y=alt.Y('Forecast Value:Q', stack='normalize'),
        color='Country_Type:N',
        tooltip=['Year', 'Country_Type', alt.Tooltip('Forecast Value', format='.2f')]
    ).properties(title='Normalized Forecast Value by Country Type Over Years').interactive()

    top_n = 10
    chart5_df = filtered_df.groupby('Area')['Forecast Value'].sum().nlargest(top_n).reset_index()
    chart5 = alt.Chart(chart5_df).mark_bar().encode(
        x=alt.X('Forecast Value:Q'),
        y=alt.Y('Area:N', sort='-x'),
        tooltip=['Area', 'Forecast Value']
    ).properties(title=f'Top {top_n} Countries by Total Forecast Value').interactive()

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart1, width='stretch')
        st.altair_chart(chart3, width='stretch')
        st.altair_chart(chart5, width='stretch')
    with col2:
        st.altair_chart(chart2, width='stretch')
        st.altair_chart(chart4, width='stretch')
