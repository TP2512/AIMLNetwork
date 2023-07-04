from datetime import datetime, timedelta, timezone
#
# import plotly.express as px
#
# df = px.data.gapminder().query("country in ['Canada', 'Botswana']")
# print(df)
#
# fig = px.line(df, x="lifeExp", y="gdpPercap", color="country", text="year")
# fig.update_traces(textposition="bottom right")
# fig.show()

start_time_ = datetime(2022, 3, 13, 12, 3, 24, 226)
print(start_time_)
d = start_time_.replace(microsecond=0)
print(d)
