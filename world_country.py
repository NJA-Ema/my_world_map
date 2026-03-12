import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import requests
import pandas as pd

app = dash.Dash(__name__)
server = app.server

# ১. ড্রপডাউন সার্চ বারের জন্য দেশের তালিকা তৈরি
df = px.data.gapminder().query("year == 2007").sort_values("country")
country_options = [{'label': name, 'value': name} for name in df['country'].unique()]

# ২. অ্যাপ লেআউট
app.layout = html.Div([
    html.H1("বিশ্ব এনসাইক্লোপিডিয়া (বাংলা ভার্সন)", style={'textAlign': 'center', 'fontFamily': 'SolaimanLipi, Arial', 'color': '#2c3e50'}),
    
    html.Div([
        html.Label("দেশের নাম দিয়ে সার্চ করুন:", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='country-search',
            options=country_options,
            placeholder="একটি দেশ সিলেক্ট করুন...",
            style={'width': '100%'}
        ),
    ], style={'width': '60%', 'margin': '0 auto 20px auto'}),

    dcc.Graph(
        id='world-map',
        figure=px.choropleth(
            df, 
            locations="iso_alpha",
            color="lifeExp", 
            hover_name="country",
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Plasma
        ).update_layout(
            clickmode='event+select', 
            margin={"r":0,"t":0,"l":0,"b":0}
        )
    ),

    html.Div(id='country-info', style={
        'padding': '30px', 'marginTop': '20px', 'border': '2px solid #3498db',
        'borderRadius': '15px', 'backgroundColor': '#fcfcfc', 'minHeight': '200px'
    })
], style={'padding': '20px'})

# ৩. লজিক (Callback)
@app.callback(
    Output('country-info', 'children'),
    [Input('world-map', 'clickData'),
     Input('country-search', 'value')]
)
def update_info(clickData, search_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.H3("শুরু করতে ম্যাপে ক্লিক করুন অথবা সার্চ করুন।", style={'color': '#888', 'textAlign': 'center'})
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    country_name = None

    if trigger_id == 'country-search' and search_value:
        country_name = search_value
    elif trigger_id == 'world-map' and clickData:
        point = clickData['points'][0]
        country_name = point.get('hover_name') or point.get('location')

    if not country_name:
        return "সঠিক দেশ নির্বাচন করুন।"

    try:
        # API থেকে ডেটা সংগ্রহ
        api_url = f"https://restcountries.com/v3.1/name/{country_name}?fullText=true"
        if len(country_name) == 3 and country_name.isupper():
            api_url = f"https://restcountries.com/v3.1/alpha/{country_name}"
            
        res = requests.get(api_url)
        data = res.json()[0]

        # --- বাংলা উইকিপিডিয়া লিঙ্ক তৈরি ---
        # আমরা 'bn.wikipedia.org' ব্যবহার করছি
        # দেশের সাধারণ নাম (Common Name) দিয়ে লিঙ্ক তৈরি করা হচ্ছে
        wiki_name = data['name']['common']
        wiki_link_bn = f"https://bn.wikipedia.org/wiki/{wiki_name.replace(' ', '_')}"

        return html.Div([
            html.Div([
                html.H2(f"🌍 {data['name']['common']}", style={'display': 'inline-block', 'marginRight': '20px'}),
                html.Img(src=data['flags']['png'], style={'height': '60px', 'borderRadius': '5px'})
            ]),
            html.Hr(),
            html.Div([
                html.P([html.Strong("👥 জনসংখ্যা: "), f"{data.get('population', 0):,}"]),
                html.P([html.Strong("🏛️ রাজধানী: "), f"{data.get('capital', ['N/A'])[0]}"]),
                html.P([html.Strong("📍 মহাদেশ: "), f"{data.get('region', 'N/A')}"]),
                html.P([html.Strong("💰 মুদ্রা: "), f"{', '.join(data.get('currencies', {}).keys())}"]),
                html.P([html.Strong("🗣️ ভাষা: "), f"{', '.join(data.get('languages', {}).values())}"]),
                html.P([html.Strong("📅 স্বাধীনতা: "), "হ্যাঁ" if data.get('independent') else "না"]),
            ], style={'columnCount': 2}),
            html.Br(),
            html.A("📖 বাংলা উইকিপিডিয়াতে বিস্তারিত পড়ুন ➔", 
                   href=wiki_link_bn, target="_blank", 
                   style={
                       'padding': '12px', 'backgroundColor': '#27ae60', 'color': 'white', 
                       'borderRadius': '8px', 'textDecoration': 'none', 'display': 'inline-block', 'fontWeight': 'bold'
                   })
        ])
    except:
        return f"{country_name} এর তথ্য লোড করতে সমস্যা হয়েছে।"

if __name__ == '__main__':
    app.run(debug=True)
