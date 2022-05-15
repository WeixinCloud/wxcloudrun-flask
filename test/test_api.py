import unittest
import requests


test_url = 'http://127.0.0.1:8056'


class TestApi(unittest.TestCase):

    def test_fanyi(self):
        test_case = {
            "apple": "苹果",
            1: "1",
            "苹果": "苹果",
            "": ""
        }
        for k, v in test_case.items():
            res = requests.post(test_url + '/api/fanyi', json={
                "fanyi_content": k
            })
            data = res.json().get("data")
            self.assertEqual(data, v)


if __name__ == '__main__':
    unittest.main()
