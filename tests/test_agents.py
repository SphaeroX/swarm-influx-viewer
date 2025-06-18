import os
import sys
import importlib
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def setup_module(module):
    os.environ['INFLUX_BUCKET'] = 'test_bucket'
    os.environ['INFLUX_URL'] = 'http://localhost'
    os.environ['INFLUX_TOKEN'] = 'token'
    os.environ['INFLUX_ORG'] = 'org'


def test_influx_query_inserts_bucket_when_missing():
    with patch('influxdb_client.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        query = '|> range(start: -1h)'  # missing from(bucket)
        agents.influx_query(query)

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert called_query.startswith('from(bucket: "test_bucket")')


def test_influx_query_replaces_empty_bucket():
    with patch('influxdb_client.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        query = 'from(bucket: "")\n  |> range(start: -1h)'
        agents.influx_query(query)

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert 'from(bucket: "test_bucket")' in called_query
