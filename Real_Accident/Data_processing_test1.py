import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import folium
import glob, os
#---------------------------------------------------------------------------------
data = pd.read_csv("AIS_2019_09_07_region_2.csv")
data_all_MMSI_list = data.MMSI.unique().tolist()
accident_ship_MMSI = 538007762
accident_ship_index = data_all_MMSI_list.index(accident_ship_MMSI)
data_all_MMSI_list.pop(accident_ship_index)
data_all_MMSI_list.insert(0, accident_ship_MMSI)
MMSI_array = data_all_MMSI_list
total_ship_number = 20
scatter = 0
path = './Real_data/2019_09_07/'
scatter_file = glob.glob(os.path.join(path, "segment_oneship*_2019_09_07_region_2.csv"))
print(scatter_file)

for i in range(1,total_ship_number+1):
    shipnumber = i
    data_processing_1 = 1
    filename_processing_1 = ("./Real_data/2019_09_07/data_oneship_%d_2019_09_07_region_2.csv" %(shipnumber))
    data_processing_2 = 0
    filename_processing_2 = ("./Real_data/2019_09_07/data_oneship_%d_2019_09_07_new_region_2.csv" %(shipnumber))
    draw = 0
    filename_draw = ("./Real_data/2019_09_07/segment_oneship_%d_2019_09_07_region_2.csv" %(shipnumber))
    mapname_draw = ('./Map/2019_09_07/ocean_map_%d_2019_09_07_region_2.html' %(shipnumber))

    MMSI = MMSI_array[shipnumber-1]
    #----------------------------------------------------------------------------------
    if (data_processing_1 == 1):
        path = './'
        file = glob.glob(os.path.join(path, "AIS_2019_09_07_region_2.csv"))
        print(file)
        Data = []
        for f in file:
            data = pd.read_csv(f)
            #316001251,367542320,366961250
            data = data[data["MMSI"] == MMSI]
            data = data.iloc[:, :6]
            Data.append(data)
        data_oneship = pd.concat(Data)
        #------------------------------------------------------------------------------------
        data_oneship.to_csv(filename_processing_1)
        print(data_oneship)
        data_processing_1 = 0
        data_processing_2 = 1
#------------------------------------------------------------------------------------------------
    if(data_processing_2 == 1):
        data_oneship = pd.read_csv(filename_processing_1)
        data_oneship['BaseDateTime'] = data_oneship['BaseDateTime'].replace("T", " ", regex=True)
        data_oneship['BaseDateTime'] = pd.to_datetime(data_oneship['BaseDateTime'])
        data_oneship = data_oneship.sort_values(by=['BaseDateTime'], ascending=True)
        
        data_oneship.to_csv(filename_processing_2)
        data_processing_2 = 0
        draw = 1
#---------------------------------------------------------------------------------------------
    if(draw == 1):
        data_oneship = pd.read_csv(filename_processing_2)
        data_oneship['BaseDateTime'] = pd.to_datetime(data_oneship['BaseDateTime'])
        data_oneship.set_index('BaseDateTime', inplace=True)
        #-----------------------------------------------------------------------------------
        if (data_oneship.shape[0] > 0) is False:
            continue
        latitude = data_oneship.iloc[0].at['LAT']
        longitude = data_oneship.iloc[0].at['LON']
        location = data_oneship.values[:, 4:6].tolist()
        #------------------------------------------------------------------------------------
        # Instantiate a feature group for the incidents in the dataframe
        incidents = folium.map.FeatureGroup()

        # Loop through the each data point and add each to the incidents feature group
        # 2019 01 
        for lat, lng, in zip(data_oneship.LAT, data_oneship.LON):
            incidents.add_child(
                folium.CircleMarker(
                    [lat, lng],
                    radius=0.05, # define how big you want the circle markers to be
                    color='black',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.4
                )
            )

        # Add incidents to map
        ocean_map = folium.Map(location=[latitude, longitude], zoom_start=11)
        ocean_map.add_child(incidents)
        #-----------------------------------------------------------------------------------
        N = 140
        M = 0
        start_time=[]
        end_time=[]
        mean_speed=[]
        var_speed=[]
        mean_direction=[]
        var_direction=[]
        MMSI_list=[]
        data_oneship['cos_COG'] = data_oneship['COG'].map(lambda x: math.cos(math.radians(x)))
        data_oneship['sin_COG'] = data_oneship['COG'].map(lambda x: math.sin(math.radians(x)))
        for i in range(M, N):
            segment_name = ("./Real_data/2019_09_07/segment_ship_%d_period_%d_2019_09_07_region_2.csv" %(shipnumber,i))
            p = pd.Period('2019-09-07', freq = '10T')
            start = (p+i).to_timestamp()
            end = (p+i+1).to_timestamp()
            segment = data_oneship[start:end]
            if (segment.shape[0] > 4) is False:
                continue
            segment.to_csv(segment_name)
            
            #2:4
            location_segment = segment.values[:, 3:5].tolist()
            print(segment)
            if len(location_segment) == 0:
                continue
            mean_speed.append(segment['SOG'].mean())
            var_speed.append(segment['SOG'].var())
            mean_direction.append(segment['COG'].mean())
            var_direction.append((segment['cos_COG'].mean()**2 + segment['sin_COG'].mean()**2)**0.5)
            start_time.append(start)
            end_time.append(end)
            MMSI_list.append(MMSI)

            if (i % 2) == 0:
                color_segment = 'red'
            elif (i % 2) == 1:
                color_segment = 'green'
            folium.PolyLine(
                    location_segment,
                    weight=2.5,
                    color=color_segment,
                    opacity=1
                    ).add_to(ocean_map)
        
        segment_oneship_list ={ 'MMSI' : MMSI_list,
                                'start time' : start_time,
                                'end time' : end_time,
                                'mean speed' : mean_speed,
                                'var speed' : var_speed,
                                'mean_direction' : mean_direction,
                                'var_direction' : var_direction
                                } 
        segment_oneship = pd.DataFrame(segment_oneship_list)
        
        max_speed_segment = segment_oneship['mean speed'].max()
        min_speed_segment = segment_oneship['mean speed'].min()
        segment_oneship['max_speed'] = max_speed_segment
        segment_oneship['min_speed'] = min_speed_segment
        #if max_speed_segment == min_speed_segment :
        #    draw = 0
        #    continue
        #segment_oneship = segment_oneship.drop(segment_oneship[segment_oneship['max_speed'] == segment_oneship['min_speed']].index)
        #segment_oneship['Nor_speed'] = segment_oneship.apply(lambda x:(x['mean speed']-x['min_speed']) / (x['max_speed']-x['min_speed']), axis=1)
        segment_oneship.to_csv(filename_draw)
        print(segment_oneship)

        #draw_polylines(location, data_oneship['SOG'], ocean_map)
        ocean_map.save(mapname_draw)
        draw = 0
#----------------------------------------------------------------------------
if scatter == 1:
    segment_Data = []
    for f in scatter_file:
        segment_data = pd.read_csv(f)
        segment_Data.append(segment_data)
    segment_moreship = pd.concat(segment_Data)
    print(segment_moreship)
    #----------------------------------------------------------------------------------------------------------------------------
    lgd = 'segment of ' + str(total_ship_number) + ' ship'
    ship=plt.scatter(segment_moreship[:]["Nor_speed"], 
            1-segment_moreship[:]["var_direction"], s=3, c='orange', label=lgd)
    plt.xlabel("Normalized mean speed during each 10 min")
    plt.ylabel("Normalized variance of direction during each 10 min")
    plt.legend()
    plt.show()

def draw_polylines(points, speeds, map):
    colors = [speed_color(x) for x in speeds]
    n = len(colors)
    # Need to have a corresponding color for each point
    if n != len(points):
        raise ValueError
    i = 0
    j = 1
    curr = colors[0]
    while i < n and j < n:
        if colors[i] != colors[j]:
            line = folium.PolyLine(points[i:j], color=curr, weight=2.5, opacity=1)
            line.add_to(map)
            curr = colors[j]
            i = j
        j += 1
    if i < j:
        folium.PolyLine(points[i:j], color=curr, weight=2.5, opacity=1).add_to(map)


def speed_color(speed):
    if speed < 0:
        raise ValueError
    elif speed >= 0 and speed < 10:
        return 'green'
    elif speed >= 10 and speed < 18:
        return 'yellow'
    else:
        return 'red'
