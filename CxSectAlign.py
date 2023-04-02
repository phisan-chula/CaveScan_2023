#
#
# CxSectAlign : product cross-section from alignment
#
#
import pandas as pd 
import geopandas as gpd 
from pathlib import Path
from sklearn.cluster import DBSCAN
from shapely.geometry import LineString,Point
import numpy as np


class Alignment:
    def __init__(self ):
        pass

def MakeTrav( FILE ):
    SWAP = ( [ 37,38 ] )
    REMOV = ( 88 )
    COL = [ 'E','N','Z','Lat','Long' ]
    df = gpd.read_file( FILE )
    df.crs='EPSG:4326'
    print( f'Num of points: {len(df)}' )
    X =  df[['E','N']].to_numpy()
    cluster = DBSCAN( eps=0.01, min_samples=5 ).fit( X )
    df['label'] = cluster.labels_ 
    ##############################################
    clus = [] ; pnts = []
    for label,grp in df.groupby( 'label' ):
        if label == -1: continue
        #print( f'{label} : {len(grp)}...')
        mean = grp[COL].mean()
        std  = grp[COL].std()
        clus.append( [ label, len(grp), np.sqrt( std.E**2+std.N**2),std.Z, 
                         mean.E, mean.N, mean.Z ] )
        pnts.append( Point( mean.Long, mean.Lat) )  
    dfCLUS = gpd.GeoDataFrame( clus, crs='EPSG:4326', geometry=pnts ) 
    dfCLUS.columns = ['Label','NumPnt', 'stdHor','stdVer', 'E', 'N', 'Z', 'geometry' ]
    for col in ['stdHor','stdVer']:
        dfCLUS[col] =  dfCLUS[col].round(2)
    trav = []
    for i in range( len(dfCLUS)-1 ):
        fr = dfCLUS.iloc[i]
        to = dfCLUS.iloc[i+1]
        trav.append( LineString([fr.geometry,to.geometry]) )
    dfTRAV = gpd.GeoDataFrame( crs='EPSG:4326' , geometry=trav )    
    #import pdb ; pdb.set_trace()
    return dfCLUS, dfTRAV, df

###########################################################
###########################################################
###########################################################
STATION = Path( r'Data/ControlThamluang/CRNN/CRNN.shp' )
CACHE   = Path( r'./CACHE' )
CACHE.mkdir(parents=True, exist_ok=True)

dfSTAT,dfALIGN,dfPnt =  MakeTrav( STATION )

TRAV_FILE = CACHE / f'{STATION.stem}.gpkg'
dfSTAT.to_file(  TRAV_FILE, driver='GPKG', layer='Station')
dfALIGN.to_file( TRAV_FILE, driver='GPKG', layer='Traverse')
dfPnt.to_file( TRAV_FILE, driver='GPKG', layer='Point')

import pdb ; pdb.set_trace()
