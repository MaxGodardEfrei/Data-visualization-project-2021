import streamlit as st
import pandas as pd
import numpy as np
import time
from matplotlib import pyplot as plt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

df = pd.read_csv('df.csv')
df2 = pd.read_csv('df2.csv')
df['date'] = pd.to_datetime(df['date'])


st.title('Data visualization project : 2018/01/29 - 2018/10/24')
st.title('Max GODARD - 2021')

col1, col2 = st.columns([1,1])
with col1:
    st.image('qrcode Linkedin.png', caption='Linkedin', width=200)
with col2:
    st.image('qrcode github.png', caption='Github', width=200)

st.info("Total data : " + str(df.shape[0]))
st.info("Average datas per day : " + str(round(df.groupby(df['date'].dt.date).size().mean())))

firstday = pd.to_datetime('2018-01-29', utc= True)
lastday = pd.to_datetime('2018-10-24', utc= True)

select = st.radio('select',['general values','day values','both'])
if (select != 'general values'):
    date_input = st.date_input('date', value=firstday, min_value=firstday, max_value=lastday)

red_values = ["Studio", "Epita (1st campus)", "Bus station", "Mall", "Tram stop",
                                            "City center", "City center", "Parents: Clermont-Ferrand",
                                            "Epita (2nd campus)", "Disneyland", "Epita (Paris campus)"]

def newMap():
    fmap = folium.Map(location=[45.745096, 4.817937], zoom_start=14)
    mCluster = MarkerCluster(name="Markers").add_to(fmap)
    dfValue = None
    if(select != 'general values'):
        dfValue = df.loc[(df['date'].dt.date == date_input)].reset_index().drop(columns='index')
        rows, cols = dfValue.shape
        for i in range(rows):
            marker = folium.Marker(location=[dfValue['latitude'][i], dfValue['longitude'][i]], popup=str(dfValue['date'][i]))
            marker.add_to(mCluster)
    rows, cols = df2.shape
    if(select != 'day values'):
        for i in range(1, rows):
            for i in range(1, rows):
                folium_icon = None
                if df2.iloc[i]['label'] in red_values:
                    folium_icon = folium.Icon(color='red')
                else:
                    folium_icon = folium.Icon(color='gray')
                marker = folium.Marker(location=[df2.iloc[i]['latitude'], df2.iloc[i]['longitude']],
                                       popup=df2.iloc[i]['label'], icon=folium_icon)
                marker.add_to(fmap)
    if(select == 'general values' or dfValue.shape[0] != 0):
        folium_static(fmap)
    if(select != 'general values'):
        return dfValue
    else:
        return None

dfValue = newMap()

def zones(i):
    return df2['label'][i+1]

weekday = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
month = ['January','Febuary','March','April','May','June','July','August','September','October','November','December']

def strTime(time):
    hours, seconds = divmod(time * 60, 3600)
    minutes, seconds = divmod(seconds, 60)
    return "{:02.0f}:{:02.0f}".format(hours, minutes)

def intTime(time_str):
    return time.strptime(time_str,'%H:%M').tm_min + 60*time.strptime(time_str,'%H:%M').tm_hour



#st.write(day())
if (select != 'general values'):
    dfValue2 = dfValue.loc[dfValue['zones'].shift(-1) != dfValue['zones']]
    dfValue2 = dfValue2.append(dfValue.loc[dfValue['zones'].diff() != 0], ignore_index=True)
    dfValue2 = dfValue2.sort_values(by='date', ascending=True).reset_index().drop(columns='index')
    dfValue2['end'] = dfValue2['date'].shift(-1)
    dfValue2 = dfValue2.drop(dfValue2[dfValue2.index % 2 !=0].index)
    dfValue2 = dfValue2.rename(columns={"date":"begin"}).reset_index().drop(columns='index')

    dfValue2['time'] = (dfValue2['end'] - dfValue2['begin'])/np.timedelta64(1,'m')
    dfValue2['time'] = dfValue2['time'].apply(strTime)
    dfValue2['begin'] = pd.to_datetime(pd.Series(dfValue2['begin'])).dt.strftime("%H:%M")#begin : only time
    dfValue2['end'] = pd.to_datetime(pd.Series(dfValue2['end'])).dt.strftime("%H:%M")#end : only time
    dfValue2 = dfValue2[['begin', 'end','time', 'zones']]
    dfValue2['zones'] = dfValue2['zones'].apply(zones)
    st.info('total data : ' + str(dfValue.shape[0]))
    st.dataframe(dfValue2)#show dataframe to show the day

if(select != 'day values'):
    df3 = df.loc[df['zones'].shift(-1) != df['zones']]
    df3 = df3.append(df.loc[df['zones'].diff() != 0], ignore_index=True)
    df3 = df3.sort_values(by='date', ascending=True).reset_index().drop(columns='index')
    df3['end'] = df3['date'].shift(-1)
    df3 = df3.drop(df3[df3.index % 2 != 0].index)
    df3 = df3.rename(columns={"date": "begin"}).reset_index().drop(columns='index')
    df3['time'] = (df3['end'] - df3['begin']) / np.timedelta64(1, 'm')
    df3 = df3[['begin', 'end', 'time', 'zones']]
    df3['zones'] = df3['zones'].apply(zones)
    df3 = df3.groupby('zones').agg({'time': ['mean']})

    df3 = df3['time']#?
    df3['zones'] = df3.index#?
    df3 = df3.reset_index(drop="True")#?
    df3 = df3.rename(columns={"mean":"time"})#?
    df3 = df3[['zones','time']]#?
    df3['time'] = df3['time'].apply(strTime)

fig = plt.figure(figsize=(10, 7))  # fix size
if(select == 'general values'):
    plt.bar(df3['zones'], df3['time'].apply(intTime), color='green')
    plt.xticks(rotation=60)
    plt.xlabel("Average time spent in the same place") #time is a string : no time shown
    plt.ylabel("Time spent")
    plt.title("Place")
    for i in range(len(df3['zones'])):
        plt.text(i-0.35, df3['time'].apply(intTime)[i]+10, strTime(df3['time'].apply(intTime)[i]))


if(select != 'general values'):
    dfValue3 = dfValue2
    dfValue3['time'] = dfValue3['time'].apply(intTime)
    dfValue3 = dfValue3.groupby('zones').agg({'time': ['mean']})
    dfValue3 = dfValue3['time']# ?
    dfValue3['zones'] = dfValue3.index # ?
    dfValue3 = dfValue3.reset_index(drop="True")  # ?
    dfValue3 = dfValue3.rename(columns={"mean": "time"})  # ?
    dfValue3 = dfValue3[['zones', 'time']]  # ?
    dfValue3['time'] = dfValue3['time'].apply(strTime)

if(select == 'day values'):
    plt.bar(dfValue3['zones'], dfValue3['time'].apply(intTime), color='tomato')
    plt.xticks(rotation=60)
    plt.xlabel("Average time spent in the same place")
    plt.ylabel("Time spent")
    plt.title("Place")
    for i in range(len(dfValue3['zones'])):
        plt.text(i - 0.35, dfValue3['time'].apply(intTime)[i] + 10, strTime(dfValue3['time'].apply(intTime)[i]))

if(select == 'both'):
    df3 = df3.rename(columns={"time":"general time"})
    dfValue3= dfValue3.rename(columns={"time": "day time"})
    dfFusion = df3.merge(dfValue3,on='zones')

    plt.bar(dfFusion['zones'], dfFusion['general time'].apply(intTime),0.4, label='general time', color='green')
    plt.bar(dfFusion['zones'], dfFusion['day time'].apply(intTime),0.4, label='day time', color='tomato')
    plt.xticks(rotation=60)
    plt.legend()
    for i in range(len(dfFusion['zones'])):
        plt.text(i - 0.35, dfFusion['general time'].apply(intTime)[i] + 10, strTime(dfFusion['general time'].apply(intTime)[i]), color='green')
        plt.text(i - 0.35, dfFusion['day time'].apply(intTime)[i] + 10, strTime(dfFusion['day time'].apply(intTime)[i]), color='tomato')

st.pyplot(fig)

#begin : minuit - end : 23h59
#stats sur les stats (entre quelles heures j'ai le plus de stats, ou, quand : histogrammes)