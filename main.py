import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair

with st.echo(code_location='below'):
    data_corona = pd.read_csv("us-states.csv")
    data_corona_sum = data_corona[data_corona.date == "2022-05-12"]

    state_codes = {
        'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
        'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
        'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
        'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
        'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
        'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
        'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
        'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
        'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
    }

    data_corona_sum = data_corona_sum.replace(dict(zip(map(int, state_codes.values()), state_codes.keys())))

    data_elections = pd.read_csv("president_county_candidate.csv")

    data_elections = data_elections[data_elections.party.isin(["DEM", "REP"])]

    data_elections = data_elections.groupby(by=["state", "party"]).sum().reset_index(1).pivot(columns="party",
                                                                                              values="total_votes")
    data_elections["WINNER"] = data_elections.DEM > data_elections.REP
    data_elections.WINNER = data_elections.WINNER.replace({True: "Biden", False: "Trump"})

    data_elections = data_elections.reset_index()

    us_state_to_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "U.S. Virgin Islands": "VI"}
    data_elections.replace(us_state_to_abbrev, inplace=True)

    data_corona_sum = data_corona_sum.merge(data_elections, left_on="fips", right_on="state", how="inner")

    data_corona_sum["ratio_cases"] = data_corona_sum.cases / (data_corona_sum.DEM + data_corona_sum.REP)

    data_corona_sum_trump = data_corona_sum[data_corona_sum.WINNER == "Trump"]
    data_corona_sum_biden = data_corona_sum[data_corona_sum.WINNER == "Biden"]

    st.title('Coronavirus and political preferences in the US')
    st.header("The current situation and the dynamics")

    chart_trump = altair.Chart(data_corona_sum_trump).mark_bar().encode(
        altair.Y("cases", bin=altair.Bin(extent=[0, 10e6], step=1e6), sort="descending",
                 title="Number of COVID case on May, 12"),
        x=altair.X('count()', sort="descending", title="Republicans: Count of states"),
    )

    chart_biden = altair.Chart(data_corona_sum_biden).mark_bar().encode(
        altair.Y("cases", bin=altair.Bin(extent=[0, 10e6], step=1e6), axis=None, sort="descending"),
        x=altair.X('count()', sort="ascending", scale=altair.Scale(domain=[0, 13]), title="Democrats: Count of states"),
    )
    st.altair_chart((chart_trump | chart_biden).properties(title="The distribution of COVID across the states"),
                    use_container_width=True)
    st.write("Press play to see the dynamics")
    fig = px.scatter(data_corona, x="deaths", y="cases", animation_frame="date", animation_group="state",
                     log_y=True, log_x=True, hover_name="state", range_x=[1, 1e6], range_y=[1, 1e7 + 5e6],
                     title="The dynamics of COVID")
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1
    fig

    option = st.selectbox(
        'Choose the state to see the time-series',
        np.unique(data_corona.state))

    state = data_corona[data_corona.state == option]

    state["diff_cases"] = state.cases.diff()

    state["diff_deaths"] = state.deaths.diff()

    state.diff_deaths[state.diff_deaths < 0] = 0
    state.diff_deaths.fillna(0, inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=state.date,
            y=state.cases,
            name="Cumulative number of cases"
        ), secondary_y=False, )

    fig.add_trace(
        go.Bar(
            x=state.date,
            y=state.diff_deaths,
            name="Number of deaths per day"
        ), secondary_y=True)

    fig.update_layout(
        yaxis2=dict(
            titlefont=dict(
                color="red"
            ),
            tickfont=dict(
                color="red"
            ),
            range=[0, max(state.diff_deaths) * 3]
        )
    )
    st.plotly_chart(fig)
    st.header("My hypothesis")
    st.write("Look at these two maps. Aren't they similar?")
    radio1 = st.radio(
        "",
        ('Corona', 'Elections'))

    map1 = px.choropleth(data_corona_sum,
                         locations='fips',
                         locationmode="USA-states",
                         scope="usa",
                         color='ratio_cases',
                         color_continuous_scale="bluered",
                         title="Coronavirus Situation on May,12"
                         )

    map2 = px.choropleth(data_elections,
                         locations='state',
                         locationmode="USA-states",
                         scope="usa",
                         color='WINNER',
                         color_discrete_sequence=["red", "blue"],
                         title="President Elections 2020"
                         )

    if radio1 == 'Elections':
        st.plotly_chart(map2)
    else:
        st.plotly_chart(map1.update_layout(
            coloraxis_colorbar=dict(
                title="Ratio of cases to population")))
    st.header("Hypothesis confirmation")
    data_corona_sum["rep_dem_ration"] = data_corona_sum.REP / data_corona_sum.DEM
    fig, ax = plt.subplots()
    sns.scatterplot(data=data_corona_sum, x="rep_dem_ration", y="ratio_cases", hue="WINNER", ax=ax,
                    palette=["red", "blue"])
    ax.set(xlabel="Number of people voted for Trump in 2020 (relatively)", ylabel="Ratio of cases to population")
    st.pyplot(fig)

    data_corona_sum['color'] = np.where(data_corona_sum.WINNER == "Trump", "red", "blue")

    radio2 = st.radio(
        "What's your favorite movie genre",
        ('Order 1', 'Order 2'))

    if radio2 == 'Order 2':
        fig, ax = plt.subplots()
        sns.regplot(data=data_corona_sum, x="rep_dem_ration", y="ratio_cases", ci=None, order=2, ax=ax,
                    scatter_kws={"facecolor": data_corona_sum['color']})
        ax.set(xlabel="Number of people voted for Trump in 2020 (relatively)", ylabel="Ratio of cases to population",title="Regression")
        st.pyplot(fig)
    else:
        fig, ax = plt.subplots()
        sns.regplot(data=data_corona_sum, x="rep_dem_ration", y="ratio_cases", ci=None, order=1, ax=ax,
                    scatter_kws={"facecolor": data_corona_sum['color']})
        ax.set(xlabel="Number of people voted for Trump in 2020 (relatively)", ylabel="Ratio of cases to population",title="Regression")
        st.pyplot(fig)
