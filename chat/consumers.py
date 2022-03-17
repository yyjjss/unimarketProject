import json
import logging

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from unimarket.models import ChatInfo, ChatRoom, Mark


# from asgiref.sync import async_to_sync
#from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
logger = logging.getLogger(__name__)

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        logger.info("self : "+str(self))
        logger.info("roomname : "+str(self.room_name))
        logger.info("groupName : "+str(self.room_group_name))

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        senderMemNo = text_data_json['senderMemNo']
        chatNo = text_data_json['chatNo']
        
        dtoChatRoom = ChatRoom.objects.get(chatNo=chatNo)
        # 상세 채팅내용 저장
        dtoChatInfo = ChatInfo(
                    chatNo = chatNo,
                    itemNo = dtoChatRoom.itemNo,
                    sellMemNo = dtoChatRoom.sellMemNo,
                    buyMemNo = dtoChatRoom.buyMemNo,
                    fromSender = senderMemNo,
                    chatContent = message,
                    chatRead = 0,
                )
        dtoChatInfo.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'senderMemNo' : senderMemNo
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        senderMemNo = event['senderMemNo']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'senderMemNo' : senderMemNo
        }))

# class ChatConsumer(WebsocketConsumer):
    # def connect(self):
        # self.accept()
        #
    # def disconnect(self, close_code):
        # pass
        #
    # def receive(self, text_data):
    #
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        # senderMemNo = text_data_json['senderMemNo']
        # chatNo = text_data_json['chatNo']
        #
        # dtoChatRoom = ChatRoom.objects.get(chatNo=chatNo)
        # # 상세 채팅내용 저장
        # dtoChatInfo = ChatInfo(
                    # chatNo = chatNo,
                    # itemNo = dtoChatRoom.itemNo,
                    # sellMemNo = dtoChatRoom.sellMemNo,
                    # buyMemNo = dtoChatRoom.buyMemNo,
                    # fromSender = senderMemNo,
                    # chatContent = message,
                    # chatRead = 0,
                # )
        # dtoChatInfo.save()
        #
        # self.send(text_data=json.dumps({
            # 'message': message,
            # 'senderMemNo' : senderMemNo
        # }))
    
class AlarmConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("alarmConnect")
        self.groupname="shares"
        
        async_to_sync(self.channel_layer.group_add)(
            self.groupname,
            self.channel_name
        )
        
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.groupname,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        alarm = text_data_json['alarm']
        
        if alarm == "applyAlarm" :  # 거래완료 신청 알람
            message = text_data_json['message']
            sellMemNo = text_data_json['sellMemNo']
            buyMemNo = text_data_json['buyMemNo']
            buyusername = text_data_json['buyusername']
            itemNo = text_data_json['itemNo']
            itemTitle = text_data_json['itemTitle']
            content = text_data_json['content']
            chatNo = text_data_json['chatNo']
            # recontent = str(content)+"_"+str(buyusername)+"_"+str(sellMemNo)
            
            # 알람데이터 업데이트
            dtoMark = Mark(
                    markNo = "sh"+str(sellMemNo)+"_"+str(chatNo)+"_"+str(itemNo),
                    memNo = buyMemNo,  # 거래자 
                    markStat = 4,
                    markContent = content,
                )
            dtoMark.save()
            
            async_to_sync(self.channel_layer.group_send)(
                self.groupname,
                {
                    'type': 'alarm_message',
                    'message': message,
                    'sellMemNo' : sellMemNo,
                    'buyMemNo' : buyMemNo,
                    'itemNo' : itemNo,
                    'itemTitle' : itemTitle,
                    'chatNo' : chatNo,
                    'buyusername' : buyusername,
                    'alarm' : alarm,
                }
            )
        elif alarm == "refuseAlarm" : # 거래완료 거절 알람
            logger.info("refuseAlarm")
            message = text_data_json['message']
            sellMemNo = text_data_json['sellMemNo']
            buyMemNo = text_data_json['buyMemNo']
            chatNo = text_data_json['chatNo']
            itemNo = text_data_json['itemNo']
            # itemTitle = text_data_json['itemTitle']
            content = text_data_json['content']
            logger.info("refuse_massage: "+str(message))
            # 알람데이터 업데이트
            dtoMark = Mark(
                    markNo = "re"+str(itemNo)+"_"+str(chatNo),
                    memNo = sellMemNo,  # 거래자 
                    markStat = 5,
                    markContent = content,
                )
            dtoMark.save()
            # 해당 데이터 존재여부 확인 
            # markCnt = Mark.objects.filter(markNo="re"+str(itemNo), memNo=sellMemNo).count()
            # if markCnt == 0 :
            #
            # else :
                # dtoMark = Mark.objects.get(markNo="re"+str(itemNo), memNo=sellMemNo)
                # # 어쩔까... ?
           
            async_to_sync(self.channel_layer.group_send)(
                self.groupname,
                {
                    'type': 'alarm_message',
                    'message': message,
                    'sellMemNo' : sellMemNo,
                    'buyMemNo' : buyMemNo,
                    'itemNo' : itemNo,
                    'chatNo' : chatNo,
                    'alarm' : alarm,
                }
            )
        elif alarm == "sellAlarm":  
            message = text_data_json['message']
            sellMemNo = text_data_json['sellMemNo']
            
            async_to_sync(self.channel_layer.group_send)(
                self.groupname,
                {
                    'type': 'alarm_message',
                    'message': message,
                    "sellMemNo" : sellMemNo, 
                    'alarm' : alarm,
                }
            )
        elif alarm == "cancelAlarm" : 
            message = text_data_json['message']
            sellMemNo = text_data_json['sellMemNo']
            buyMemNo = text_data_json['buyMemNo']
            itemNo = text_data_json['itemNo']
            chatNo = text_data_json['chatNo']
            
            dtoMark = Mark(
                    markNo = "cc"+str(itemNo),
                    memNo = sellMemNo,  # 판매자 
                    markStat = 4,
                    markContent = itemTitle,
                )
            dtoMark.save()
            
            async_to_sync(self.channel_layer.group_send)(
                self.groupname,
                {
                    'type': 'alarm_message',
                    'message': message,
                    'sellMemNo' : sellMemNo,
                    'buyMemNo' : buyMemNo,
                    'itemNo' : itemNo,
                    'chatNo' : chatNo,
                    'alarm' : alarm,
                }
            )
        elif alarm == "priceAlarm" :
            message = text_data_json['message']
            sellMemNo = text_data_json['sellMemNo']
            buyMemNo = text_data_json['buyMemNo']
            itemNo = text_data_json['itemNo']
            chatNo = text_data_json['chatNo']

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.groupname,
                {
                    'type': 'alarm_message',
                    'message': message,
                    'sellMemNo' : sellMemNo,
                    'buyMemNo' : buyMemNo,
                    'itemNo' : itemNo,
                    'chatNo' : chatNo,
                    'alarm' : alarm,
                }
            )

    # Receive message from room group
    def alarm_message(self, event):
        alarm = event['alarm']
        
        if alarm == "applyAlarm" :
            message = event['message']
            sellMemNo = event['sellMemNo']
            buyMemNo = event['buyMemNo']
            itemNo = event['itemNo']
            chatNo = event['chatNo']
            buyusername = event['buyusername']
            itemTitle = event['itemTitle']
            logger.info("연결보내기 : "+str(self))
            
                # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': message,
                'sellMemNo' : sellMemNo,
                'buyMemNo' : buyMemNo,
                'itemNo' : itemNo,
                'chatNo' : chatNo,
                'buyusername' : buyusername,
                'itemTitle' : itemTitle,
                'alarm' : alarm,
            }))
        elif alarm == "sellAlarm" :
            message = event['message']
            sellMemNo = event['sellMemNo']
            logger.info("연결보내기 : "+str(self))
            
                # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': message,
                'sellMemNo' : sellMemNo,
                'alarm' : alarm,
            }))
        else : 
            message = event['message']
            sellMemNo = event['sellMemNo']
            buyMemNo = event['buyMemNo']
            itemNo = event['itemNo']
            chatNo = event['chatNo']
            logger.info("연결보내기 : "+str(self))
            
            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'message': message,
                'sellMemNo' : sellMemNo,
                'buyMemNo' : buyMemNo,
                'itemNo' : itemNo,
                'chatNo' : chatNo,
                'alarm' : alarm,
            }))

    
# no 실시간
# class AlarmConsumer(WebsocketConsumer):   
    # def connect(self):
        # # self.groupname="shares"
        # self.accept()
        #
    # def disconnect(self, close_code):
        # pass
        #
    # def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # alarm = text_data_json['alarm']
        #
        # if alarm == "applyAlarm" :  # 거래완료 신청 알람
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # buyMemNo = text_data_json['buyMemNo']
            # buyusername = text_data_json['buyusername']
            # itemNo = text_data_json['itemNo']
            # itemTitle = text_data_json['itemTitle']
            # content = text_data_json['content']
            # chatNo = text_data_json['chatNo']
            # # recontent = str(content)+"_"+str(buyusername)+"_"+str(sellMemNo)
            #
            # # 알람데이터 업데이트
            # dtoMark = Mark(
                    # markNo = "sh"+str(sellMemNo)+"_"+str(chatNo)+"_"+str(itemNo),
                    # memNo = buyMemNo,  # 거래자 
                    # markStat = 4,
                    # markContent = content,
                # )
            # dtoMark.save()
            #
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # 'sellMemNo' : sellMemNo,
                # 'buyMemNo' : buyMemNo,
                # 'itemNo' : itemNo,
                # 'itemTitle' : itemTitle,
                # 'chatNo' : chatNo,
                # 'buyusername' : buyusername,
                # 'alarm' : alarm,
            # }))
        # elif alarm == "refuseAlarm" : # 거래완료 거절 알람
            # logger.info("refuseAlarm")
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # chatNo = text_data_json['chatNo']
            # itemNo = text_data_json['itemNo']
            # itemTitle = text_data_json['itemTitle']
            # content = text_data_json['content']
            #
            # # 알람데이터 업데이트
            # dtoMark = Mark(
                    # markNo = "re"+str(itemNo)+"_"+str(chatNo),
                    # memNo = sellMemNo,  # 거래자 
                    # markStat = 5,
                    # markContent = content,
                # )
            # dtoMark.save()
            # # 해당 데이터 존재여부 확인 
            # # markCnt = Mark.objects.filter(markNo="re"+str(itemNo), memNo=sellMemNo).count()
            # # if markCnt == 0 :
            # #
            # # else :
                # # dtoMark = Mark.objects.get(markNo="re"+str(itemNo), memNo=sellMemNo)
                # # # 어쩔까... ?
                #
                #
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # "sellMemNo" : sellMemNo, 
                # 'alarm' : alarm,
            # }))
        # elif alarm == "sellAlarm":  # 
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # "sellMemNo" : sellMemNo, 
                # 'alarm' : alarm,
            # }))
        # elif alarm == "cancelAlarm" : 
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # buyMemNo = text_data_json['buyMemNo']
            # itemNo = text_data_json['itemNo']
            # chatNo = text_data_json['chatNo']
            #
            # dtoMark = Mark(
                    # markNo = "cc"+str(itemNo),
                    # memNo = sellMemNo,  # 판매자 
                    # markStat = 4,
                    # markContent = itemTitle,
                # )
            # dtoMark.save()
            #
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # 'sellMemNo' : sellMemNo,
                # 'buyMemNo' : buyMemNo,
                # 'itemNo' : itemNo,
                # 'chatNo' : chatNo,
                # 'alarm' : alarm,
            # }))
        # elif alarm == "priceAlarm" :
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # buyMemNo = text_data_json['buyMemNo']
            # itemNo = text_data_json['itemNo']
            # chatNo = text_data_json['chatNo']
            #
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # 'sellMemNo' : sellMemNo,
                # 'buyMemNo' : buyMemNo,
                # 'itemNo' : itemNo,
                # 'chatNo' : chatNo,
                # 'alarm' : alarm,
            # })) 
        # elif alarm == "soldOutAlarm" :
            # message = text_data_json['message']
            # sellMemNo = text_data_json['sellMemNo']
            # buyMemNo = text_data_json['buyMemNo']
            # itemNo = text_data_json['itemNo']
            # chatNo = text_data_json['chatNo']
            # logger.info("연결보내기 : "+str(self))
            #
            # self.send(text_data=json.dumps({
                # 'type': 'share_message',
                # 'message': message,
                # 'sellMemNo' : sellMemNo,
                # 'buyMemNo' : buyMemNo,
                # 'itemNo' : itemNo,
                # 'chatNo' : chatNo,
                # 'alarm' : alarm,
            # }))
        
        
