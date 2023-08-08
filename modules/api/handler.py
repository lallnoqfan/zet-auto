from typing import Dict

from requests import get, post, Response

from .models import DvachThread, Post
from .schemas import DvachPostingSchemaIn


class DvachAPIHandler:

    def __init__(self, usercode: str, usercode_auth: str, passcode_auth: str):

        self.usercode = usercode
        self.cookies = {
            'usercode_auth': usercode_auth,
            'passcode_auth': passcode_auth,
        }

    def update_cookies(self, cookies: Dict[str, str]) -> None:
        self.cookies.update(cookies)

    def get_thread(self, board: str, thread_num: str | int) -> DvachThread | None:

        r = self.get_thread_raw(board, thread_num)

        if r.status_code != 200:
            return None

        posts = r.json()['threads'][0]['posts']

        posts = [Post(
            num=p.get('num'),
            number=p.get('number'),
            comment=p.get('comment'),
            datetime=p.get('date'),
            sage=p.get('email') == 'mailto:sage',
        ) for p in posts]

        return DvachThread(posts=posts)

    @staticmethod
    def get_thread_raw(board: str, thread_num: str | int) -> Response:

        url = f'https://2ch.hk/{board}/res/{thread_num}.json'
        r = get(url)

        return r

    def post_posting(self, schema: DvachPostingSchemaIn,
                     headers: Dict = None, cookies: Dict = None) -> Response:

        url = 'https://2ch.hk/user/posting'

        schema.usercode = self.usercode
        data = schema.to_data()

        if not headers:
            headers = {}
        headers.update({'Content-Type': data.content_type})

        if not cookies:
            cookies = dict()
        cookies.update(self.cookies)

        return post(url, data=data, headers=headers, cookies=cookies)
