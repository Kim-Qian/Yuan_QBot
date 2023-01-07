# Yuan_QBot
此程序将“源”接入了QQ
QQ接收端采用了ｇｏ－ｃｑｈｔｐ：https://github.com/Mrs4s/go-cqhttp
支持多轮对话，但所有对话都被存在一个列表里，导致在于A对话时，若对话内容与B相似，会调用与B的历史对话
