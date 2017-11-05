# -*- coding: utf-8 -*-
from backtradercn.settings import settings as conf
from backtradercn.libs.log import logging
from werobot.client import Client


logger = logging.getLogger(__name__)


class WeChatClient(Client):
    def send_all_text_message(self, content):
        '''
        群发文本消息。

        :param content: 消息正文
        :return: 返回的 JSON 数据包
        '''
        return self.post(
            url='https://api.weixin.qq.com/cgi-bin/message/mass/sendall',
            data={
                'filter': {
                    'is_to_all': True,
                },
                'text': {
                    'content': content,
                },
                'msgtype': 'text'
            }
        )


if __name__ == '__main__':
    client = WeChatClient({
        'APP_ID': conf.WECHAT_APP_ID,
        'APP_SECRET': conf.WECHAT_APP_SECRET,
    })
    response = client.send_all_text_message('just test')
    logger.debug(response)
