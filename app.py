import plotly.graph_objects as do
import pandas as pd
import numpy as np
import json
from matplotlib.colors import Normalize
from matplotlib import cm
import streamlit as st

@st.cache
def load_data():
	return pd.read_csv('multi_data_edit.csv')
	
@st.cache
def load_json():
	with open('regions_data.json') as f:
     		map_json = json.load(f)
     	
	return map_json

def centroid(count,map_json):
	lon, lat =[], []
	for k in range(count):
        	geometry = map_json['features'][k]['geometry']

        	if geometry['type'] == 'Polygon':
            		coords=np.array(geometry['coordinates'][0])
        	elif geometry['type'] == 'MultiPolygon':
            		coords=np.array(geometry['coordinates'][0][0])

        	lon.append(sum(coords[:,0]) / len(coords[:,0]))
        	lat.append(sum(coords[:,1]) / len(coords[:,1]))

	return lon, lat

def shape_source(map_json):
	sources = []	
	for feat in map_json['features']:
		sources.append({'type':'FeatureCollection',
				'features':[feat]})
	
	return sources

def fscalarmappable(cmap, cmin, cmax):
	colormap = cmap #cm.get_cmap(cmap)
	norm = Normalize(vmin=cmin, vmax=cmax)
	return cm.ScalarMappable(cmap=colormap, norm=norm)
	
def fcolorscale(sm, count, cmin, cmax):
	xrange = np.linspace(0, 1, num= count)
	values = np.linspace(cmin, cmax, num= count)
	return [[i, 'rgba' + str(sm.to_rgba(v, bytes=True, norm=True))] for i,v in zip(xrange, values)]
	
def fsortscale(data,colorscale):
	data_sort = data.sort_values(by='Data',ascending=True)
	face_color = []
	for name,color in zip(list(data_sort['Name']),colorscale):
		face = {'name': name, 'colored': color[1]}
		face_color.append(face)
	mapped = sorted(face_color, key= lambda k:k['name'])
	return [d['colored'] for d in mapped]
	
def main():
	map_token = 'pk.eyJ1IjoibmVpbHRoZWdyZWF0ZXN0IiwiYSI6ImNrM2ZqMmhvNjAzN2QzbW5uaHQyamo5NGkifQ.l53kgbZcDGY8U8xHkSWv0w'
	map_style = 'mapbox://styles/neilthegreatest/ck5uymies43dg1iqko1h41v1f'

	datax = load_data()
	map_json = load_json()

	#with open('regions_data.json') as f:
     		#map_json = json.load(f)

	count = len(map_json['features'])

	region_names = [map_json['features'][i]['properties']['REGION'] for i in range(count)]
	
	st.title('Philippine Choropleths')
	st.markdown('A collection of choropleth maps of various data obtained from PSA Openstat.')
	
	x= 'Percentage of Food Expenditure to Total Family Expenditure (2015)'
	y= 'Percentage of Barangays with Health Stations (2015)'
	z= 'Proportion of Fully Immunized Children (2015)'
	a= 'Child Dependency Ratio (2015)'
	b= 'Secondary Net Enrolment Rate (2015)'
	c= 'Secondary Completion Rate (2015)'
	d= 'Functional Literacy Rate of the Population 10-64 Years Old (2013)'
	e= 'Functional Literacy rate of 10 to 19 Year Olds (2013)'
	
	option1 = st.selectbox('What do you want to know?', [x,y,z,a,b,c,d,e])
	
	if option1 == x:
		datay = datax[['Name','Lat', 'Lon', x]].copy()
	elif option1 == y:
		datay = datax[['Name','Lat', 'Lon', y]].copy()
	elif option1 == z:
		datay = datax[['Name','Lat', 'Lon', z]].copy()
	elif option1 == a:
		datay = datax[['Name','Lat', 'Lon', a]].copy()
	elif option1 == b:
		datay = datax[['Name','Lat', 'Lon', b]].copy()
	elif option1 == c:
		datay = datax[['Name','Lat', 'Lon', c]].copy()
	elif option1 == d:
		datay = datax[['Name','Lat', 'Lon', d]].copy()
	elif option1 == e:
		datay = datax[['Name','Lat', 'Lon', e]].copy()
	
	data = datay.rename(columns={option1:'Data'})
	
	dff = data.set_index(['Name'])
	
	s= 'Greens'
	t= 'Reds'
	u= 'Blues'
	v = 'viridis'
	w = 'Pastel1'
	
	option2 = st.radio('Try a different color', [s,t,u,v,w])
	
	st.header(option1)
	
	if (option1 == d) or (option1 == e):
		st.markdown('*Provinces from Region VIII (Eastern Visayas) were excluded due to the devastation brought about by Typhoon Yolanda.*')

	colormap = option2
	cmin = 0 #dff['Data'].min()
	cmax = 100 #dff['Data'].max()

	sources = shape_source(map_json)
	lons, lats = centroid(count,map_json)

	sm = fscalarmappable(colormap, cmin, cmax)
	colorscale = fcolorscale(sm, count, cmin, cmax)
	face = fsortscale(data,colorscale)

	layers = (
		[{
		'sourcetype':'geojson',
		'source':sources[k],
		'below':"",
		'type':'line',
		'line':{'width':1},
		'color':'black'
		} for k in range(count)] +
	
		[{
		'sourcetype':'geojson',
		'source':sources[k],
		'below':'water',
		'type':'fill',
		'color': face[k],
		'opacity':0.8
		 }for k in range(count)]
	)

	plot = do.Figure()

	plot.add_trace(
		do.Scattermapbox(
			lat= list(data['Lat']),
			lon= list(data['Lon']),
			mode= 'markers',
			text= ['<b>{}</b>'.format(x) + '<br>Percentage: ' + '{}'.format(y) for x,y in zip(list(data['Name']),list(data['Data']))],
			hoverinfo='text',
			showlegend=False,
			marker={
				'size':1,
				'color':'white'
				}
		)
	)

	plot.update_layout(
		width= 800,
		height=1000,
		hovermode='closest',
		hoverdistance = 30,
		mapbox= do.layout.Mapbox(
			accesstoken= map_token,
			layers=layers,
			center= do.layout.mapbox.Center(
				lat=11.9674,
				lon=121.9248
				),
			zoom=5.3,
			style= map_style
		),
		margin= do.layout.Margin(l=0,r=0,t=0,b=0)
	)

	st.plotly_chart(plot, use_container_width=True)
	
	st.markdown('Data Source: PSA Openstat | Viz by: nvqa')

if __name__ == '__main__':
	main()

