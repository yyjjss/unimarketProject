// 챗팅에 따른 화면 전환 ajax
$(document).ready(function(){
	$(".chatSend").on(
		"click", function(){
			var chatNo = $("#chatNo").val()
			var memNo = $("#memNo").val()
			var sendContent = $(".sendContent").val()
			let param= {
					"chatNo" : chatNo,
					"memNo" : memNo,
					"sendContent" : sendContent
				}
			  $.ajax(
					  {
						  url : "updateChatInfo",
						  type : "POST",
						  data : JSON.stringify(param),
						  dataType : "json",
							success : function(data){
								var result = ' '; // 채팅 <ul class="chat">
								console.log(data);
								//result +='<ul class="chat">'
								// 채팅 리스트
								$.each(data["dtoChat"], function(index, chat){
									if(chat["fromSender"] == memNo){
										result += '<li class="me">'
										result += '<div class="entente">'
										result += '<div class="me-img">'
										result += '<img src="/media/'+data["memList"][0].proImg+'" alt="본인이미지" /></div>'
										console.log(data["memList"][0].proImg);
										result += '<h6>'+data["memList"][0].nickname+'</h6>'
										result += '<div class="message">'
										result += chat["chatContent"]+'</div>'
										result += '</div>'
										result += '</li>'
									}else{
										result += '<li class="you">'
										result += '<div class="your-img">'
										result += '<img src="/media/'+data["otherList"][0].proImg+'" alt="상대방이미지" /></div>'
										result += '<div class="entente">'
										result += '<h6>'+data["otherList"][0].nickname+'</h6>'
										result += '<div class="message">'
										result += chat["chatContent"]+'</div>'
										result += '</div>'
										result += '</li>'
									}
								})
								//result +='</ul>'
								$(".chat").html(result)
							},
							error : function(request, status, error){
								//console.log("code = "+ request.status + " error = " + error); // 실패 시 처리
								//console.log("error")
							}
						}
					);
		}
	);
});


var openWin;
$(document).ready(function(){
	$(".kakaoMap").on(
		"click", function(){
			// window.name = "부모창 이름"; 
            window.name = "parentForm";
			url="uniSearchMap"
			openWin = open(url, "confirm", "childForm", "toolbar=no, menubar=no, scrollbar=no, width=600, height=600");
			
		}
	);
});