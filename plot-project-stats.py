#!python
import plotly.io as pio
pio.orca.config.use_xvfb = True
import plotly.express as px
import pandas as pd
df = pd.read_csv('/tmp/num-checks.csv')

MONTH = {
'Jan': "01",
'Feb': "02",
'Mar': "03",
'Apr': "04",
'May': "05",
'Jun': "06",
'Jul': "07",
'Aug': "08",
'Sep': "09",
'Oct': "10",
'Nov': "11",
'Dec': "12"
}
def parse_date (date):
  elements = date.strip().split(' ')
  return f"{elements[4]}-{MONTH[elements[1]]}-{elements[2]} {elements[3]}"

df['Date'] = list(map(parse_date, df['Date']))
fig = px.area(df, x='Date', y='Checks', range_y=[130,230], range_x=['2017-12-06','2021-12-31'])
fig.write_image("public/num_checks.svg")
