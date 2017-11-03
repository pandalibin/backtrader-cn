# -*- coding: utf-8 -*-

from werobot.client import Client


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
        'APP_ID': 'wx5e8e3c4779887f32',
        'APP_SECRET': 'd4624c36b6795d1d99dcf0547af5443d',
    })
    response = client.send_all_text_message('just test')
    print(response)
