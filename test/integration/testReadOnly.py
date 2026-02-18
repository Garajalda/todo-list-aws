import os
import requests
import unittest
import json

BASE_URL = os.environ.get("BASE_URL")

class TestReadOnly(unittest.TestCase):

    def setUp(self):
        self.assertIsNotNone(BASE_URL, "BASE_URL no configurada")

    def test_list_todos(self):
        response = requests.get(BASE_URL + "/todos")
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        todos = json.loads(json_response["body"])

        self.assertIsInstance(todos, list)

        if len(todos) > 0:
            todo = todos[0]
            self.assertIn("id", todo)
            self.assertIn("text", todo)
            self.assertIn("checked", todo)

    def test_get_existing_if_available(self):
        response = requests.get(BASE_URL + "/todos")
        json_response = response.json()
        todos = json.loads(json_response["body"])

        if len(todos) > 0:
            todo_id = todos[0]["id"]

            response = requests.get(BASE_URL + f"/todos/{todo_id}")
            self.assertEqual(response.status_code, 200)
