from dialogue_V2 import chat
from inspurai import Yuan, set_yuan_account,Example
from flask import request, Flask
import requests

set_yuan_account("", "")  # 输入您申请的账号和手机号
yuan = Yuan(engine="dialog",
            input_prefix="我：“",
            input_suffix="”",
            output_prefix="答：“",
            output_suffix="”",
            append_output_prefix_to_query=True)
qq_no = 机器人的qq号，为数字
#while True :
#    que = input("我：")
#    ans = chat(yuan,que)
#    print("Yuan: ",ans)

# 创建一个服务，把当前这个python文件当做一个服务
server = Flask(__name__)

# qq消息上报接口，qq机器人监听到的消息内容将被上报到这里
@server.route('/', methods=["POST"])
def get_message():
    #print("--------------")
    if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
        #print("1111111111111111")
        uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
        message = request.get_json().get('raw_message')  # 获取原始信息
        sender = request.get_json().get('sender')  # 消息发送者的资料
        print("收到私聊消息：")
        print(message)
        ans = chat(yuan,message)
        send_private_message(uid, ans)
    if request.get_json().get('message_type') == 'group':  # 如果是群消息
        gid = request.get_json().get('group_id')  # 群号
        uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
        message = request.get_json().get('raw_message')  # 获取原始信息
        # 判断当被@时才回答
        if str("[CQ:at,qq=%s]" % qq_no) in message:
            sender = request.get_json().get('sender')  # 消息发送者的资料
            print("收到群聊消息：")
            print(message)
            message = str(message).replace(str("[CQ:at,qq=%s]" % qq_no), '')
            ans = chat(yuan,message)
            #send_private_message(uid, ans)
            send_group_message(gid, ans, uid)  # 将消息转发到群里
    if request.get_json().get('post_type') == 'request':  # 收到请求消息
        print("收到请求消息")
        request_type = request.get_json().get('request_type')  # group
        uid = request.get_json().get('user_id')
        flag = request.get_json().get('flag')
        comment = request.get_json().get('comment')
#        print("配置文件 auto_confirm:" + str(config_data['qq_bot']['auto_confirm']) + " admin_qq: " + str(
#            config_data['qq_bot']['admin_qq']))
        if request_type == "friend":
            print("收到加好友申请")
            print("QQ：", uid)
            print("验证信息", comment)
            set_friend_add_request(flag, "true")
        if request_type == "group":
            print("收到群请求")
            sub_type = request.get_json().get('sub_type')  # 两种，一种的加群(当机器人为管理员的情况下)，一种是邀请入群
            gid = request.get_json().get('group_id')
            if sub_type == "add":
                # 如果机器人是管理员，会收到这种请求，请自行处理
                print("收到加群申请，不进行处理")
            elif sub_type == "invite":
                print("收到邀请入群申请")
                print("群号：", gid)
                set_group_invite_request(flag, "true")
    return "ok"

# 发送私聊消息方法 uid为qq号，message为消息内容
def send_private_message(uid, message):
    try:
        res = requests.post(url="http://localhost:8600" + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            print("私聊消息发送成功")
        else:
            print(res)
            print("私聊消息发送失败，错误信息：" + str(res['wording']))
    except Exception as error:
        print("私聊消息发送失败")
        print(error)

# 发送群消息方法
def send_group_message(gid, message, uid):
    try:
        message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url="http://localhost:8600" + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            print("群消息发送成功")
        else:
            print("群消息发送失败，错误信息：" + str(res['wording']))
    except Exception as error:
        print("群消息发送失败")
        print(error)

# 处理邀请加群请求
def set_group_invite_request(flag, approve):
    try:
        requests.post(url="http://localhost:8600" + "/set_group_add_request",
                      params={'flag': flag, 'sub_type': 'invite', 'approve': approve})
        print("处理群申请成功")
    except:
        print("处理群申请失败")

# 处理好友请求
def set_friend_add_request(flag, approve):
    try:
        requests.post(url="http://localhost:8600" + "/set_friend_add_request",
                      params={'flag': flag, 'approve': approve})
        print("处理好友申请成功")
    except:
        print("处理好友申请失败")

if __name__ == '__main__':
    server.run(port=5555, host='0.0.0.0', use_reloader=False)
