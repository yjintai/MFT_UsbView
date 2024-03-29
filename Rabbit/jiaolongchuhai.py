import time
import datetime
import pandas as pd
import logging

import sqlalchemy
from sqlalchemy import exc
import pymysql

databasename = 'msstock'
sqlenginestr='mysql+pymysql://root:root@127.0.0.1/'+databasename+'?charset=utf8mb4'

pd.set_option('expand_frame_repr', False)

# 获取指定日期的分析统计结果
def jiaolongchuhai (date_str):

    #analysisfilename = basedir+'/dailyanalysis/'+ str(date_now) + '_jiaolongchulai.csv'
    engine = sqlalchemy.create_engine(sqlenginestr)
    fmt = '%Y%m%d'
    date=datetime.datetime.strptime(date_str,fmt)
    date_list=date -datetime.timedelta(days = 5)
    date_list_str = date_list.strftime(fmt)

    # 读取limit up ts_code
    sql = '''SELECT * FROM msstock.tb_daily_limit_up where trade_date = '%s' and list_date < '%s';''' %(date_str,date_list_str)
    df = pd.read_sql_query(sql, engine)
    df.fillna(0, inplace=True)
    df.replace('nan ', 0, inplace=True)
    df_output = pd.DataFrame()
    for index, row in df.iterrows():
        sql1='''SELECT * FROM msstock.tb_daily_data where ts_code = '%s' and trade_date < '%s' order by trade_date desc limit 10;''' %(row['ts_code'],date_str)
        df1 = pd.read_sql_query(sql1, engine)
        df1.fillna(0, inplace=True)
        df1.replace('nan ', 0, inplace=True)
        if (row['low'] >  df1['high'][0])  & (row['amount'] < df1['amount'][0]):
            df_output = df_output.append(df.loc[[index]])
    #print (df_output)
    return df_output

def meas_jiaolongchuhai (data):
    if data.shape[0] == 0:
        print ('Empty Data!')
        return
    engine = sqlalchemy.create_engine(sqlenginestr)
    df_output = pd.DataFrame(columns=('ts_code','name','trade_date','pct_chg_date_1', 'pct_chg_date_2', 'pct_chg_date_3', 'pct_chg_date_4', 'pct_chg_date_5'))
    i =0
    for index, row in data.iterrows():
        sql1='''SELECT * FROM msstock.tb_daily_data where ts_code = '%s' and trade_date > '%s' order by trade_date limit 5;''' %(row['ts_code'],row['trade_date'])
        df1 = pd.read_sql_query(sql1,engine)
        df1.fillna(0, inplace=True)
        df1.replace('nan ', 0, inplace=True)
        df_output = df_output.append({'ts_code':row['ts_code'],'name':row['name'],'trade_date':row['trade_date']}, ignore_index= True)   
        for j in range(df1.shape[0]):
            df_output['pct_chg_date_%d' %(j+1)][i] = df1['pct_chg'][j]
        i +=1
    print(df_output)
    logging.debug (df_output)

if __name__ == '__main__':
    logging.debug('start...')
    print('analyze daily data')
    '''
    fmt = '%Y%m%d'
    start_date = '20210422'
    end_date = '20210425'
    start=datetime.datetime.strptime(start_date,fmt)
    end=datetime.datetime.strptime(end_date,fmt)
    '''
    end = datetime.datetime.now()
    start=end -datetime.timedelta(days = 2)
    
    for i in range((end - start).days+1):
        date = start + datetime.timedelta(days=i)
        date_str = date.strftime('%Y%m%d')
        print(date_str)  
        data=jiaolongchuhai(date_str)
        meas_jiaolongchuhai(data)
    print('end')