import pandas as pd
import numpy as np
from sklearn import preprocessing
import pydeck as pdk
from data import db

class eda:
    def __init__(self, df_move, df_fix):
        self.df_move = self._pre(df_move)
        self.df_fix = self._pre(df_fix)

    # 데이터 전처리
    def _pre(self, df):
        df = df.replace(np.nan, '0', regex=True) # nan 값은 0으로 처리
        df = df.drop(['pollutant'], axis=1) # 'pollutant'칼럼 drop
        df = df.astype(float) #float 형태로 변환
        df2 = df.drop(['lon', 'lat'], axis=1).reset_index() # 위경도 값까지 정규화되면 안돼서 drop, reset_index는 concat을 위한 부분(concat은 인덱스 기준으로 붙임)
        df3 = df.loc[:, ['lon', 'lat']].reset_index() # drop한 위경도
        df2 = df2.drop(['index'], axis=1)
        df3 = df3.drop(['index'], axis=1)
        # log 변환
        log_df2 = np.log1p(df2)
        # min-max
        x = log_df2.values.astype(float)
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        df2 = pd.DataFrame(x_scaled)
        df2.rename(columns={0: 'emission'}, inplace=True)
        df = pd.concat([df2, df3], axis=1) # 전처리된 emission부분(df2)과 위경도정보(df3)을 concat (axis=1을 추가하면 가로방향으로 concat)
        df.dropna(axis=0)
        return df

    # 데이터 시각화 (시각화할 library로 pydeck 채택 -> pydeck은 input을 data frame 형태로 받음)
    def display(self):
        state = pdk.ViewState(
            latitude=37.323,
            longitude=126.732,
            zoom=11,
            max_zoom=16,
            pitch=45,
            bearing=0)

        move = pdk.Layer(
            "HeatmapLayer",
            data=self.df_move,
            opacity=0.9,
            get_position=["lon", "lat"],
            get_weight='emission',
            pickable=True
        )

        fix = pdk.Layer(
            'ScatterplotLayer',
            data=self.df_fix ,
            get_position='[lon, lat]',
            get_radius=50,
            get_fill_color='[255*emission, 15*emission,255]',
            pickable=True,
            auto_highlight=True)
        fix.extruded = True
        fix.elevation_scale = 3  # default 1

        r = pdk.Deck(
            layers=[move, fix],
            initial_view_state=state)

        r.to_html('111.html')

# 코드에서 달라지는(= 수정해야하는) 부분은 여기
# list엔 오염물질명 / 다른 오염물질을 보고 싶으면 여기만 고치면 됨 (코드 안에서 하나 하나 고칠 필요 X)
list='VOCs'
# data base에서 data 가져올때 (1) 이동차/배출구 (2) 오염물질 종류 선택
df_move= db("select  * from EDMS.MOVECARDB WHERE POLNAME= '{0}'".format(list))
df_move.rename(columns={5: 'pollutant', 7: 'emission', 10: 'lon', 11: 'lat', 15: 'time'}, inplace=True)
# lon/lat/emission/pollutant 형식으로 data frame 생성 (나중에 pollutant는 버림)
df_move = df_move[['pollutant', 'emission', 'lon', 'lat']]

df_fix= db("select  * from EDMS.MOVECARDB WHERE POLNAME= '{0}'".format(list))
df_fix.rename(columns={5: 'pollutant', 7: 'emission', 10: 'lon', 11: 'lat', 15: 'time'}, inplace=True)
df_fix = df_fix[['pollutant', 'emission', 'lon', 'lat']]

# 객체 a 생성, input으로 이동차, 배출구 데이터
a=eda(df_move, df_fix)
output = a.display()



