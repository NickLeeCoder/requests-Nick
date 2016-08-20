# requests-Nick

##首先是get(url)函数
###这是我们自定义的根据URL获取数据的函数
###get函数的具体步骤如下:
- 解析URL  拿到具体的请求协议 host  端口号  请求路径
- 根据第一步获得的请求协议创建socket对象
- 用新建的socket实例与服务器建立连接  这时候需要传入一个tuple(host port)
- 创建一个request  这是必须是一个标准的http请求 严格按照http请求来新建
- 'GET 路径 HTTP版本\r\nhost:服务器域名(在这里能添加部分属性)\r\n'
- 'GET 路径 HTTP版本\r\nhost:服务器域名\r\nUser-Agent:dsauidsbdsba\r\ncookies:dhausbd\r\nContentType:text/html\r\n\r\n'

- 用新建的socket实例发送请求到服务器(这就是一个简单的client) 注意py3发送的是byte py2 发送的是字符串
- 利用函数response_by_socket(s) 拿到服务器返回的响应  这里拿到的是是byte类型
- byte转成str后  利用函数parsed_response解析str类型的服务器响应 得到返回的数据
###格式为(状态码 响应头(header) 响应体(body))  而其中body就是我们需要的制作网页爬虫的HTML源码

####其实这就是requests 库的实现原理
####我要做的就是 进一步封装其中的request请求 把headers给封装起来  方便设置

####函数response_by_socket
####其实就是根据传入的socket实例s  利用while循环接收服务器的响应数据
####然后进行返回

####函数parsed_respons
####对服务器返回的数据进行响应的解析....
####最主要的就是进行字符串的split...
