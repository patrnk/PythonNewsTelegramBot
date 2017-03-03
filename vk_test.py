import vk
import unittest
import os

class TestVkRequest(unittest.TestCase):
    
    def test_make_api_request_without_access_token(self):
        output = vk.make_vk_api_request('users.get', user_ids=1, fields='screen_name')
        self.assertEqual(output['response'][0]['screen_name'], 'durov')

    def test_make_api_request_with_access_token(self):
        token = os.environ.get('VK_ACCESS_TOKEN')
        output = vk.make_vk_api_request('users.get', access_token=token)
        self.assertEqual(len(output['response']), 1)

    def test_groups_search_valid(self):
        access_token = os.environ.get('VK_ACCESS_TOKEN')
        count = 10
        output = vk.groups_search(access_token, query='VK', type='page', count=count)
        self.assertEqual(len(output), count)
        for group in output:
            self.assertIsInstance(group, dict)

    def test_groups_search_invalid(self):
        count = 10
        with self.assertRaises(vk.VkRequestError):
            vk.groups_search('bad access token', query='VK', type='page', count=count)

    def test_wall_get(self):
        access_token = os.environ.get('VK_ACCESS_TOKEN')
        count = 10
        output = vk.wall_get(access_token, owner_id=1, filter='owner', count=count)
        self.assertEqual(len(output), count)
        for post in output:
            self.assertIsInstance(post, dict)


if __name__ == '__main__':
    unittest.main()
