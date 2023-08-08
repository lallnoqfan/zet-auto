from typing import List, Dict

from pydantic import BaseModel
from requests_toolbelt import MultipartEncoder

from .models import ImageFile


class DvachPostingSchemaIn(BaseModel):
    board:   str
    thread:  str | int = ''
    comment: str = ''

    op_mark: int = 1
    subject: str = ''
    name:    str = ''
    email:   str = ''
    tags:    str = ''

    oekaki_image:    str = ''
    oekaki_metadata: str = ''
    makaka_id:       str = ''
    makaka_answer:   str = ''

    task:         str = 'post'
    submit:       str = 'Ответ'
    captcha_type: str = '2chcaptcha'
    usercode:     str = ''
    code:         str = ''

    files: List[ImageFile] = []

    def to_dict(self) -> Dict:
        data = self.dict()  # TODO: remove deprecated method usage
        return data

    def to_data(self) -> MultipartEncoder:
        data = self.to_dict()
        del data['files']

        data = [(key, data[key]) for key in data]
        if self.files:
            data += [file.to_field() for file in self.files]

        return MultipartEncoder(fields=data)
