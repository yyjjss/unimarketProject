
$("document").ready(function(){
	//var memNo = '{{memNo}}';
	//var memNo =  sessionStorage.getItem("memNo");
	var memNo = document.getElementById("memNo").value;
	console.log("memNo:"+memNo);
	alarmSocket = new WebSocket(
               `ws://${window.location.host}/ws/uniBase`
           );
    alarmSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var alarm = data['alarm'];
        
        if(alarm == "applyAlarm"){	//거래완료 신청 알람
        	if(memNo == data['buyMemNo']){
        		var message = data['message'];
    	        var sellMemNo = data['sellMemNo'];
    	        var buyMemNo = data['buyMemNo'];
    	        var itemNo = data['itemNo'];
    	        var itemTitle = data['itemTitle'];
    	        var buyusername = data['buyusername'];
    	        var chatNo = data['chatNo'];
    	        console.log(data['buyMemNo'])
    	        console.log(itemTitle)
	        	console.log("send : "+message);
	        	if(!confirm(message)){	// 거래완료 취소에 따른 실시간 알람 
	        		console.log("refuseAlarm");
	        		alarmSocket.send(JSON.stringify({
	    			    //alarmSocket.send(JSON.stringify({
	    	            	'message': buyusername+"님께서 거래확정을 거절하셨습니다.\n\n 상품 : "+itemTitle,
	    	            	"sellMemNo" : sellMemNo,
	    	            	"buyMemNo" : buyMemNo,
	    	            	"chatNo" : chatNo, 
	    	            	"itemNo" : itemNo, 
	    	            	"itemTitle" : itemTitle, 
	    	            	"content" : "상품 ["+itemTitle+"]의 거래확정을 거래자["+buyusername+"]님께서 거절하셨습니다.", 
	    	    			"alarm" : "refuseAlarm", 
	    	    			//"itemUrl" : itemUrl,
	    	            }));
		    	}else{
		    		console.log("sellAlarm");
	        		alarmSocket.send(JSON.stringify({
	    			    //alarmSocket.send(JSON.stringify({
	    	            	'message': buyusername+"님께서 거래확정을 승인하셨습니다.\n\n 상품 : "+itemTitle,
	    	            	"sellMemNo" : sellMemNo,
	    	    			"alarm" : "sellAlarm", 
	    	    			//"itemUrl" : itemUrl,
	    	            }));
		    		// 거래확정에 대한 데이터 저장 : item 판매유무 flg=1 
		    		var param={
		    				"sellMemNo" : sellMemNo, 
			    			"buyMemNo" : buyMemNo,
			    			"itemNo" : itemNo,
			    			"itemTitle" : itemTitle, 
			    			"chatNo" : chatNo,
			    			}
		    		$.ajax({
	    					url : "updateBuyComplete",
	    					type : "POST",
	    					data : JSON.stringify(param),
	    					dataType : "text",
	    					success : function(data){
	    						console.log(data);
	    						window.location.href="uniPurchase"
	    					},
	    					error : function(request, status, error){
	    						console.log("code = "+ request.status + " message = " + request.responseText + " error = " + error); // 실패 시 처리
	    						console.log("error")
	    					}
		    			});
		    	}
	        }
        }
        
        if(alarm == "refuseAlarm"){	// 거래완료 거절 알람을 판매자에게 노출 
        	console.log(data['sellMemNo'])
        	if(memNo == data['sellMemNo']){
        	//if(memNo == 1){
        		console.log("거래완료 거절");
	        	var message = data['message'];
	        	// 
	        	if(alert(message) == false){	// alert 리턴값은 false
	        		
	        	}else{
	        		return false;
	        	}
        	}
        }
        if(alarm == "sellAlarm"){	// 거래완료 거절 알람을 판매자에게 노출 
        	console.log(data['sellMemNo'])
        	if(memNo == data['sellMemNo']){
        	//if(memNo == 1){
        		console.log("거래완료 승인");
	        	var message = data['message'];
	        	// 
	        	if(alert(message) == false){	// alert 리턴값은 false
	        		//location.reload();
	        	}else{
	        		//location.reload();
	        		return false;
	        	}
        	}
        }
        
        
//        if(alarm == "cancelAlarm"){ //거래취소
//        }
//        if(alarm == "priceAlarm"){ //금액변동
//        }
//        if(alarm == "soldOutAlarm"){ //판매완료
//        }
        
    };
    alarmSocket.onopen=function (e) {
      console.log("연결 성공"+memNo);
    };

    alarmSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };
    
});


