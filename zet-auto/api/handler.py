from typing import Dict

from requests import Response, get, post

from config import DvachConfig
from api.models import DvachThread, Post
from api.schemas import DvachPostingSchemaIn


class DvachAPIHandler:
    def __init__(self, usercode: str, usercode_auth: str, passcode_auth: str,
                 use_proxy: bool = False, proxy: str = None):
        self.usercode = usercode
        self.cookies = {
            'usercode_auth': usercode_auth,
            'passcode_auth': passcode_auth,
        }

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }

        self.use_proxy = use_proxy
        self.proxies = {
            "http": proxy,
            "https": proxy,
        } if self.use_proxy else None

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

    def get_thread_raw(self, board: str, thread_num: str | int) -> Response:
        url = f'{DvachConfig.BASE_URL}/{board}/res/{thread_num}.json'

        if not self.use_proxy:
            r = get(url, cookies=self.cookies, headers=self.headers)
        else:
            r = get(url, cookies=self.cookies, headers=self.headers, proxies=self.proxies)

        print(f"GET - {url} - {r}")

        return r

    def post_posting(self, schema: DvachPostingSchemaIn, headers: Dict = None, cookies: Dict = None) -> Response:
        url = f'{DvachConfig.BASE_URL}/user/posting?nc=1'

        schema.usercode = self.usercode
        data = schema.to_data()

        if not headers:
            headers = dict()
        headers.update(self.headers)
        headers.update({'Content-Type': data.content_type})

        if not cookies:
            cookies = dict()
        cookies.update(self.cookies)

        if not self.use_proxy:
            r = post(url, data=data, headers=headers, cookies=cookies)
        else:
            r = post(url, data=data, headers=headers, cookies=cookies, proxies=self.proxies)

        print(f"POST - {url} - {r}")
        print(data)
        print(r.request.headers)
        print(r)
        print()

        return r
