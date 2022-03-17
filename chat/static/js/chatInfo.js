


// 챗팅에 따른 화면 전환 ajax
function chatRoomSearch(){
	alert("click");
	var roomSearch = document.getElementById("chatRoomList").value;
	console.log(roomSearch);
	$.ajax(
			{
				url : "chatRoomSearch",
				type : "POST",
				data : {
					"roomSearch" : roomSearch,
				},
				dataType : "json",
				success : function(data){
					var result = ' '; // 채팅창 리스트<ul id="chatList">
					console.log(data);
					result +='<ul id="chatList">'
					if(data.listck == "0"){
						result +='<li>'
						result +='<h5>검색한 채팅방이 없습니다.</h5>'
						result +='</li>'
					}else{
						// 판매내역 리스트
						$.each(data["dtoChatList"], function(index, chatList){
							result +='<li>'
							result += '<img src="/media/'+chatList["itemImg"]'" alt="채팅 상품 이미지" />'
							result += '<a href="uniChatRoomInfo?chatNo='+chatList["chatNo"]+'&itemNo='+chatList["itemNo"]+'">'
							result += '<div>'
							result += '<h5>'+chatList["title"]+'</h5>'
							result += '<h6>'+chatList["memList"]+'/'+chatList["otherList"]+'</h6>'
							result += '</div>'
							result += '</a>'
							result += '</li>'
						})
					}
					
					result +='</ul>'
					$("#chatList").html(result);
				},
				error : function(request, status, error){
					console.log("code = "+ request.status + " message = " + request.responseText + " error = " + error); // 실패 시 처리
					console.log("error")
				}
			}
		);
}