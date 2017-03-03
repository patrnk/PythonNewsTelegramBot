import os
import time
import getpass
import argparse
import sys
import json
import vk

def get_vk_public_page_list(access_token, search_queries, results_per_query=20):
    public_pages = []
    for query in search_queries:
        public_pages += vk.groups_search(access_token, query=query, type='page', 
                                         count=results_per_query)
    return public_pages


def get_vk_public_page_id_set(public_page_list):
    return {page['gid'] for page in public_page_list}


def get_last_vk_community_posts(access_token, community_id, count=10):
    owner_id = -1 * community_id  # indicate that this is a community
    post_list = vk.wall_get(access_token, owner_id=owner_id, filter='owner', count=count)
    return post_list


def is_less_than_day(seconds):
    return seconds < 24 * 60 * 60


def select_latest_post(vk_post_list):
    return max(vk_post_list, key=lambda p: p['date'])


def is_lifeless_vk_page(access_token, page_id):
    number_of_posts_to_test = 5
    posts = get_last_vk_community_posts(access_token, page_id, 
                                        count=number_of_posts_to_test)
    latest_post_time_difference = time.time() - select_latest_post(posts)['date']
    if not is_less_than_day(latest_post_time_difference):
        return True
    for index, post in enumerate(posts[2:]):
        time_difference = posts[index - 1]['date'] - post['date']
        if not is_less_than_day(time_difference):
            return True
    return False


def get_group_by_id_with_description(access_token, group_id):
    return vk.group_get_by_id(access_token, group_id=group_id, fields='description')[0]


def is_spam_vk_page(access_token, page_id):
    page = get_group_by_id_with_description(access_token, page_id)
    stop_words = ['курсов', 'помощь', 'на заказ']
    for stop_word in stop_words:
        if stop_word.lower() in page['name'].lower():
            return True
        if stop_word.lower() in page['description'].lower():
            return True
    return False


def filter_vk_pages(access_token, page_id_set, is_bad_page_id):
    good_vk_page_ids = set()
    for page_id in page_id_set:
        if is_bad_page_id(access_token, page_id):
            continue
        good_vk_page_ids.add(page_id)
    return good_vk_page_ids
    

def save_data(data, outfile):
    json.dump(data, outfile)


#FIXME: move get_striped_vk_posts to the appropriate module
def form_vk_post_link(page_id, post_id):
    return "https://vk.com/wall%d_%d" % (page_id, post_id)


def strip_irrelevant_post_info(raw_post):
    return {'date': raw_post['date'],
            'text': raw_post['text'],
            'link': form_vk_post_link(raw_post['from_id'], raw_post['id']),
            }


def get_stripped_vk_posts(post_list):
    return [strip_irrelevant_post_info(post) for post in post_list]


def get_access_token():
    return os.environ.get('VK_ACCESS_TOKEN')


def print_no_access_token_error():
    print('No access token in VK_ACCESS_TOKEN environment variable.')
    print('Please see README.md on how to get it.')


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout)
    return parser


if __name__ == '__main__':
    args = get_argument_parser().parse_args()
    access_token = get_access_token()
    if token is None:
        print_no_access_token_error()
        sys.exit()
    search_queries = ['программист', 'программирование', 'Python']
    pages = get_vk_public_page_list(access_token, search_queries)
    page_ids = get_vk_public_page_id_set(pages)
    page_ids = filter_vk_pages(access_token, page_ids, is_lifeless_vk_page)
    page_ids = filter_vk_pages(access_token, page_ids, is_spam_vk_page)
    save_data(page_ids, outfile)