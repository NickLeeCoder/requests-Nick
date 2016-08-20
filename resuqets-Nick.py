
import socket
import ssl

"""
整个程序流程(add_by Nick):

首先是get(url)函数
这是我们自定义的根据URL获取数据的函数
get函数的具体步骤如下:
1/解析URL  拿到具体的请求协议 host  端口号  请求路径
2/根据第一步获得的请求协议创建socket对象
3/用新建的socket实例与服务器建立连接  这时候需要传入一个tuple(host port)
4/创建一个request  这是必须是一个标准的http请求 严格按照http请求来新建
'GET 路径 HTTP版本\r\nhost:服务器域名(在这里能添加部分属性)\r\n'
'GET 路径 HTTP版本\r\nhost:服务器域名\r\nUser-Agent:dsauidsbdsba\r\ncookies:dhausbd\r\nContentType:text/html\r\n\r\n'

5/用新建的socket实例发送请求到服务器(这就是一个简单的client) 注意py3发送的是byte py2 发送的是字符串
6/利用函数response_by_socket(s) 拿到服务器返回的响应  这里拿到的是是byte类型
7/byte转成str后  利用函数parsed_response解析str类型的服务器响应 得到返回的数据
格式为(状态码 响应头(header) 响应体(body))  而其中body就是我们需要的制作网页爬虫的HTML源码

函数response_by_socket
其实就是根据传入的socket实例s  利用while循环接收服务器的响应数据
然后进行返回

函数parsed_respons
对服务器返回的数据进行响应的解析....
最主要的就是进行字符串的切割...

其实这就是requests 库的实现原理
我要做的就是 进一步封装其中的request请求 把headers给封装起来  方便设置

"""


def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    有的时候有的函数, 它本身就美不起来, 你要做的就是老老实实写
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        # '://' 定位 然后取第一个 / 的位置来切片
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    # 默认端口
    port = port_dict[protocol]
    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        # HTTPS 协议需要使用 ssl.wrap_socket 包装一下原始的 socket
        # 除此之外无其他差别
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(r):
    """
    把 response 解析出 状态码 headers body 返回
    状态码是 int
    headers 是 dict
    body 是 str
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


# 复杂的逻辑全部封装成函数
def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(protocol)
    s.connect((host, port))

    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = response_by_socket(s)
    r = response.decode(encoding)

    status_code, headers, body = parsed_response(r)
    if status_code == 301:
        url = headers['Location']
        return get(url)
    return status_code, headers, body


# 以下 test 开头的函数是单元测试
def test_parsed_url():
    """
    parsed_url 函数很容易出错,
    所以我们写测试函数来运行看检测是否正确运行
    """
    http = 'http'
    https = 'https'
    host = 'g.cn'
    path = '/'
    test_items = [
        ('http://g.cn', (http, host, 80, path)),
        ('http://g.cn', (http, host, 80, path)),
        ('http://g.cn/', (http, host, 80, path)),
        ('http://g.cn:90', (http, host, 90, path)),
        ('http://g.cn:90/', (http, host, 90, path)),
        #
        ('https://g.cn', (https, host, 443, path)),
        ('https://g.cn:233/', (https, host, 233, path)),
    ]
    for t in test_items:
        url, expected = t
        u = parsed_url(url)
        # assert 是一个语句, 名字叫 断言
        # 如果断言成功, 条件成立, 则通过测试, 否则为测试失败, 中断程序报错
        e = "parsed_url ERROR, ({}) ({}) ({})".format(url, u, expected)
        assert u == expected, e


def test_parsed_response():
    """
    测试是否能正确解析响应
    """
    # NOTE, 行末的 \ 表示连接多行字符串
    response = 'HTTP/1.1 301 Moved Permanently\r\n' \
               'Content-Type: text/html\r\n' \
               'Location: https://movie.douban.com/top250\r\n' \
               'Content-Length: 178\r\n\r\n' \
               'test body'
    status_code, header, body = parsed_response(response)
    assert status_code == 301
    assert len(list(header.keys())) == 3
    assert body == 'test body'


def test_get():
    """
    测试是否能正确处理 HTTP 和 HTTPS
    """
    urls = [
        'http://movie.douban.com/top250',
        'https://movie.douban.com/top250',
    ]
    # 这里就直接调用了 get 如果出错就会挂, 测试得比较简单
    for u in urls:
        get(u)


def test():
    """
    用于测试的主函数
    """
    test_parsed_url()
    test_get()
    test_parsed_response()

if __name__ == '__main__':
    test()
