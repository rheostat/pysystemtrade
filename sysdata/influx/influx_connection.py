import datetime
from influxdb_client import InfluxDBClient
import pandas as pd
import pytz

from syscore.objects import arg_not_supplied
from sysdata.config.production_config import get_production_config

LIST_OF_INFLUX_PARAMS = ["influx_url", "influx_token", "influx_org"]

def influx_defaults(**kwargs):
    """
    Returns influx configuration with following precedence

    1- if passed in arguments: url, token, org - use that
    2- if defined in private_config file, use that. 
    3- if defined in system defaults file, use that.

    :return: influx db, hostname, port
    """
    # this will include defaults.yaml if not defined in private
    passed_param_names = list(kwargs.keys())
    production_config = get_production_config()
    output_dict = {}
    for param_name in LIST_OF_INFLUX_PARAMS:

        if param_name in passed_param_names:
            param_value = kwargs[param_name]
        else:
            param_value = arg_not_supplied

        if param_value is arg_not_supplied:

            param_value = getattr(production_config, param_name)

        output_dict[param_name] = param_value

    # Get from dictionary
    url = output_dict["influx_url"]
    token = output_dict["influx_token"]
    org = output_dict["influx_org"]

    return url, token, org


class InfluxClientFactory(object):

    def __init__(self):
        self.influx_clients = {}

    def get_influx_client(self, url, token, org):
        key = (url, token, org)
        if key not in self.influx_clients:
            self.influx_clients[key] = InfluxDBClient(url=url, token=token, org=org)
        return self.influx_clients[key]
            
influx_client_factory = InfluxClientFactory()

class InfluxData(object):

    def __init__(
        self,
        bucket: str,
        url: str = arg_not_supplied, 
        token: str = arg_not_supplied, 
        org: str = arg_not_supplied
    ):
        
        url, token, org = influx_defaults(
            influx_url=url,
            influx_token=token,
            influx_org=org,
        )

        self.bucket = bucket
        self.url = url
        self.token = token
        self.org = org

        client = influx_client_factory.get_influx_client(url, token, org)

        self.client = client

    @property
    def query_api(self):
        return self.client.query_api()

    def __repr__(self):
        return "InfluxDB database: url %s, token %s, org %s, bucket %s" % (
            self.url,
            self.token,
            self.org,
            self.bucket
        )

    def get_keynames(self):

        query = f"""
            import "influxdata/influxdb/schema"

            schema.tagValues(
                bucket: "{self.bucket}",
                tag: "symbol"
            )
        """

        tables = self.query_api.query(query)

        return [r.get_value() for t in tables for r in t.records]

    def read(self, code: str, start='-10y'):

        if isinstance(start, datetime.datetime):
            if start.tzinfo is None:
                start = start.replace(tzinfo=pytz.UTC)

            start = start.isoformat()

        query = f"""
            from(bucket:"{self.bucket}")
                |> range(start: {start})
                |> filter(fn: (r) => r["symbol"] == "{code}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> keep(columns: ["_time", "open", "high", "low", "close", "adjusted_close", "dividend", "split_coefficient", "volume"])
        """

        df = self.query_api.query_data_frame(query)
        df = df.set_index(pd.to_datetime(df._time)).tz_localize(None)
        df = df.drop(['_time', 'result', 'table'], axis=1)

        return df



if __name__ == '__main__':
    
    client = InfluxData(
        'alphavantage',
        url='http://192.168.86.2:8086', 
        token="5fJtUlX6ibwqN7vpRX8FnbCK5esqIc6tnNntUtLAKSgiUX-do83OXTBVmBTrtmgEZYU3cmVAzjA1QUtltHtguw==",
        org='shikona'
    )

    def display_tables(tables):

        for t in tables:
            print(t)
            for r in t.records:
                print(r)

    print(client)
    print(client.get_keynames())
    print(client.read('AAPL'))