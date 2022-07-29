from matplotlib.pyplot import title
from sqlalchemy import create_engine

import pandas as pd
import pendulum


def get_raw_data():
    df = pd.read_excel(
    '/app/input_data/historical_electricity.xlsx'
    )
    df.rename(
        columns={
            'Datum': 'register_date', 
            'Levering normaal':'consumption_normal',
            'Levering dal':'consumption_dal',
            'Teruglevering normaal':'production_normal',
            'Teruglevering dal':'production_dal',
            'Meternummer':'meter_number',
            'EAN':'ean',
            'Product':'product'
        }, inplace=True
    )
    return df


def get_pg_conn():
    conn_string = f'postgresql://da_user:password@postgres_db:5432/smartmeter_db'
    db = create_engine(conn_string)
    return db.connect()
    

def load_raw_data(conn, df):
    conn.execute("drop table if exists historical_electricity_smart_meters;")
    conn.execute("\
        create table historical_electricity_smart_meters( \
        register_date date, \
        consumption_normal decimal, \
        consumption_dal decimal, \
        production_normal decimal, \
        production_dal decimal, \
        meter_number varchar,\
        ean varchar, \
        product varchar);")
    df.to_sql('historical_electricity_smart_meters', con=conn, if_exists='append', index=False)


def data_transformation(conn):
    lag_function = '{column_name} - lag({column_name}) over \
        (partition by meter_number order by register_date)'
    conn.execute("drop table if exists historical_electricity_agg")
    conn.execute(
        f"create table historical_electricity_agg as \
        select * from ( select register_date - 1 as register_date, \
            {lag_function.format(column_name='consumption_normal')} consumption_normal, \
            {lag_function.format(column_name='consumption_dal')} consumption_dal, \
            {lag_function.format(column_name='production_normal')} production_normal, \
            {lag_function.format(column_name='production_dal')} production_dal \
        from historical_electricity_smart_meters) src \
        where src.register_date <> '2021-02-26';"
    )


def load_calendar(conn):
    start_date = pendulum.from_format('2021-02-28', 'YYYY-MM-DD')
    end_date = pendulum.from_format('2022-12-31', 'YYYY-MM-DD')
    calendar_list = []
    holiday_list = [
        '2021-01-01', '2021-04-02', '2021-04-04', '2021-04-05', '2021-04-27', '2021-05-05', '2021-05-13',
        '2021-05-23', '2021-05-24', '2021-12-25', '2021-12-26', '2022-01-01', '2022-04-15', '2022-04-17',
        '2022-04-18', '2022-04-27', '2022-05-05', '2022-05-26', '2022-06-05', '2022-06-06', '2022-12-25',
        '2022-12-26'
    ]

    while start_date <= end_date:
        calendar_list.append(
            (
                start_date.date(),
                start_date.format('dddd'),
                f"{start_date.week_of_year}-{start_date.year}",
                f"{start_date.format('MMMM')}-{start_date.year}",
                start_date.isoweekday(),
                start_date.isoweekday() in [6, 7],
                str(start_date.date()) in holiday_list
            )
        )
        start_date = start_date.add(days=1)

    df = pd.DataFrame(
        calendar_list, 
        columns = [
            'calendar_date', 'weekday_name', 'week_year', 'month_year', 'weekday_index', 'is_weekend', 'is_bank_holiday']
    )
    df.to_sql('calendar', con=conn, if_exists='replace', index=False)


def get_metric(conn, metric_type):
    if metric_type not in ['max', 'min', 'avg']:
        raise Exception("Wrong metric type, accepted values: max, min, avg")
    query = f"select weekday_name, {metric_type}(consumed_kwh) \
        from  ( select weekday_name, cal.weekday_index, heagg.consumption_normal as consumed_kwh \
                from historical_electricity_agg heagg \
                inner join calendar cal \
                on (heagg.register_date = cal.calendar_date and \
                not (cal.is_weekend = true or cal.is_bank_holiday = true)) \
                where heagg.register_date >= '2022-01-01') src \
        group by weekday_name, weekday_index"
    
    return pd.read_sql(query, conn)


def get_visuals(conn, metric_type):
    df = get_metric(conn, metric_type)
    df.plot.pie(
        x='weekday_name',
        y=metric_type,
        labels=df['weekday_name'], 
        ylabel='',
        legend=False, autopct='%1.1f%%',
        title=f'Frequency of {metric_type} consumption'
    ).figure.savefig(f'/app/visuals/frequency_{metric_type}.jpg')


def initial_load(conn):
    df = get_raw_data()
    load_raw_data(conn, df)
    data_transformation(conn)
    load_calendar(conn)


def get_all_visuals():
    conn = get_pg_conn()
    initial_load(conn)
    get_visuals(conn, 'max')
    get_visuals(conn, 'min')
    get_visuals(conn, 'avg')
    conn.close()


if __name__ == "__main__":
    get_all_visuals()

    