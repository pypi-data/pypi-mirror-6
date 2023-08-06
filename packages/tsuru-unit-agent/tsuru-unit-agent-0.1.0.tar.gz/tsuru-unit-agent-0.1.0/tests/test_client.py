import unittest
import mock

from tsuru_unit_agent.client import Client


class TestClient(unittest.TestCase):
    def test_client(self):
        client = Client("http://localhost", "token")
        self.assertEqual(client.url, "http://localhost")
        self.assertEqual(client.token, "token")

    @mock.patch("requests.get")
    def test_get_envs(self, get_mock):
        response = mock.Mock()
        response.json = mock.Mock(side_effect=lambda: {"a": "b"})
        get_mock.return_value = response
        client = Client("http://localhost", "token")
        envs = client.get_envs(app="myapp")
        self.assertDictEqual(envs, {"a": "b"})
        get_mock.assert_called_with(
            "{}/apps/myapp/env".format(client.url),
            headers={"Authorization": "bearer token"})
