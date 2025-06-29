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
    os.environ['MEASUREMENT'] = 'default_measure'


def test_influx_query_inserts_bucket_when_missing():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
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
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
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

def test_influx_query_replaces_placeholder_bucket():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        query = 'from(bucket: "INFLUX_BUCKET")\n  |> range(start: -1h)'
        agents.influx_query(query)

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert 'from(bucket: "test_bucket")' in called_query


def test_influx_query_inserts_measurement_when_missing():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        query = '|> range(start: -1h)'
        agents.influx_query(query)

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert 'r._measurement == "default_measure"' in called_query


def test_influx_query_replaces_placeholder_measurement():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        query = (
            'from(bucket: "test_bucket")\n'
            '  |> filter(fn: (r) => r._measurement == "MEASUREMENT")\n'
            '  |> range(start: -1h)'
        )
        agents.influx_query(query)

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert 'r._measurement == "default_measure"' in called_query


def test_influx_list_fields_uses_predicate():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        agents.influx_list_fields('my_measure')

        called_query = mock_query_api.query.call_args.kwargs['query']
        assert 'predicate: (r) => r._measurement == "my_measure"' in called_query


def test_ask_user_reads_input():
    with patch('builtins.input', return_value='42'):
        import agents
        importlib.reload(agents)

        result = agents.ask_user('How many?')
        assert result == '42'


def test_clarifying_agent_has_function():
    import agents
    importlib.reload(agents)

    assert agents.ask_user in agents.clarifying_agent.functions

    

def test_get_current_time_returns_iso():
    import agents
    importlib.reload(agents)

    time_str = agents.get_current_time()
    assert isinstance(time_str, str)
    assert "T" in time_str



def test_influx_query_store_caches_data():
    with patch('agents.database_manager.InfluxDBClient') as mock_client_cls:
        mock_client = MagicMock()
        mock_query_api = MagicMock()
        mock_query_api.query.return_value = []
        mock_client.query_api.return_value = mock_query_api
        mock_client_cls.return_value = mock_client

        import agents
        importlib.reload(agents)

        with patch('agents.database_manager.store_cached_data') as mock_store:
            agents.influx_query_store('fake')
            mock_store.assert_called_once()


def test_head_cached_data_returns_subset():
    import agents
    importlib.reload(agents)

    agents.store_cached_data([{'num': i} for i in range(20)])
    subset = agents.head_cached_data(5)
    assert subset['num'] == list(range(5))
