$("document").ready(function () {
	// 오른쪽 버튼 클릭시 한페이지 앞으로 
	$(".right-button").on("click", {num : 1}, pageMove);
	// 왼쪽 버튼 클릭시 한페이지 뒤로 
	$(".left-button").on("click", {num : 0}, pageMove);
});

// 버튼 "<" / ">" 로  다음페이지의  판매자 판매목록 출력 ajax   
function pageMove(e) {
	var pagecount=Number($("#pagecount").val())
	if(e.data.num == 1){ // 오른쪽 마우스(다음페이지) 
		var pageNum = Number($("#pageNum").val()) + 1;
	}else if(e.data.num == 0){ // 왼쪽 마우스(전페이지)
		var pageNum = Number($("#pageNum").val())-1;
	}
	// alert(pageNum);
	// views.py로 보낼 데이터
	let param= {
			"pageNum" : Number(pageNum),
			"sellMemNo" : $("#sellMemNo").val(),
		}
  $.ajax(
		  {
			  url : "uniSeller",
			  type : "POST",
			  data : JSON.stringify(param),
			  dataType : "json",
				success : function(data){
					var result = ' '; // 판매리스트 <nav id="navFor">
					var result2 = ' '; // 페이지번호 <div id="pageFor">
					console.log(data);
					console.log(data.count);
					// 판매내역 리스트
					$.each(data["dtoItem"], function(index, sellList){
						console.log(sellList["itemNo"]);
						result += '<a href="uniDetail?itemNo='+sellList["itemNo"]+'" class="list-group-item">'
						result += '<div class="seller-image-box">'
						// imageField를 사용할 경우 json타입으로 변환된 image.url는 string값으로 제대로된 url이 생성되지않으며, .url적용이 되지않음
						// 따라서 아래와 같이 상단 주수 /media/를 문자열에 추가하고 json타입으로 받은 이미지데이터는 .url없이 자체 데이터를 사용해야함
						if(sellList["itemImg"]){
							result += '<div class="seller-img"><img src="/media/'+sellList["itemImg"]+'" alt="상품이미지" /></div>'
						}else{
							result += '<div class="seller-img"><img src="../../static/images/market_logo_cut.png" alt="상품 이미지" /></div>'
						}
						//console.log(sellList["itemImg"]);
						result += '</div>'
						result += '<div class="seller-value">'
						result += '<h4>'+sellList["title"]
						if (sellList["sellStat"] == 0){
							result += '&nbsp;&nbsp;<span class="badge">판매중</span>' 
						} else{
							result += '&nbsp;&nbsp;<span class="badge">판매완료</span>' 
						}
						result += '</h4>'
						result += sellList["price"]+'<span>원</span>'
						result += '</div>'
						result += '</a>'
					})
					$("#navFor").html(result)
					
					// 페이지 번호
					result2 += '<input id="pageNum" type="hidden" value="'+pageNum+'">'
					if(data["startpage"] > 1){
						result2 += '<a href="javascript:void(0);" onclick="pageBlock('+data["pages"][0]+',0)"><span class="pageFont">···</span></a>&nbsp;&nbsp;'
					}
					$.each(data["pages"], function(index, page){
						if(page == data["pageNum"]){
							result2 += '<span class="pageFont"><b>'+page+'</b></span>&nbsp;&nbsp;'
						}else{
							result2 += '<a href="javascript:void(0);" onclick="pageBlock(this,2)"><span class="pageFont">'+page+'</a></span>&nbsp;&nbsp;'
						}
					})
					if(data["endpage"] < data["pagecount"]){
						result2 += '<a href="javascript:void(0);" onclick="pageBlock('+data["pages"][1]+',1)"><span class="pageFont">···</span></a>'
					}
					$("#pageFor").html(result2)
						
					if(data["pageNum"] == "1"){
						document.getElementById("lBtn").disabled = true;
					}else{
						document.getElementById("lBtn").disabled = false;
					}					
					if(data["pageNum"] == data["pagecount"]){
						console.log("pageNUm : 같댕");
						document.getElementById("rBtn").disabled = true;
					}else{
						document.getElementById("rBtn").disabled = false;
					}
				},
				error : function(request, status, error){
					//console.log("code = "+ request.status + " error = " + error); // 실패 시 처리
					//console.log("error")
				}
			}
		);
}


// 버튼외 페이지 번호 , ... 눌러 판매내역 변경
function pageBlock(ths, num){
	var pageNum=0
	if(num == 0){ // 왼쪽 ...을 눌러 전의  page_block의 첫 페이지로 이동
		pageNum = ths-2;		
	}else if(num == 1){ // 오른쪽 ...을 눌러 다음 page_block의 첫 페이지로 이동
		pageNum = ths+1;
	}else{ // a태그 번호를 눌러 페이지 이동
		pageNum = $(ths).text()
	}
	let param= {
			"pageNum" : Number(pageNum),
			"sellMemNo" : $("#sellMemNo").val(),
		}
  $.ajax(
		  {
			  url : "uniSeller",
			  type : "POST",
			  data : JSON.stringify(param),
			  dataType : "json",
				success : function(data){
					var result = ' '; // 판매리스트 <nav id="navFor">
					var result2 = ' '; // 페이지번호 <div id="pageFor">
					console.log(data);
					result +='<nav class="list-group">'
					console.log(data.count);
					console.log("page: "+data["pages"][0])
					var len = data["pages"].length
					// 판매내역 리스트
					$.each(data["dtoItem"], function(index, sellList){
						console.log(sellList["itemNo"]);
						result += '<a href="uniDetail?itemNo='+sellList["itemNo"]+'" class="list-group-item">'
						result += '<div class="seller-image-box">'
						// imageField를 사용할 경우 json타입으로 변환된 image.url는 string값으로 제대로된 url이 생성되지않으며, .url적용이 되지않음
						// 따라서 아래와 같이 상단 주수 /media/를 문자열에 추가하고 json타입으로 받은 이미지데이터는 .url없이 자체 데이터를 사용해야함
						if(sellList["itemImg"]){
							result += '<div class="seller-img"><img src="/media/'+sellList["itemImg"]+'" alt="상품이미지" /></div>'
						}else{
							result += '<div class="seller-img"><img src="../../static/images/market_logo_cut.png" alt="상품 이미지" /></div>'
						}
						//console.log(sellList["itemImg"]);
						result += '</div>'
						result += '<div class="seller-value">'
						result += '<h4>'+sellList["title"]
						if (sellList["sellStat"] == 0){
							result += '&nbsp;&nbsp;<span class="badge">판매중</span>' 
						} else{
							result += '&nbsp;&nbsp;<span class="badge">판매완료</span>' 
						}
						result += '</h4>'
						result += sellList["price"]+'<span>원</span>'
						result += '</div>'
						result += '</a>'
					})
					result +='</nav>'
					$("#navFor").html(result)
					
					// 페이지 번호
					result2 += '<div id="pageFor" style="text-align: center; padding:3%">'
					result2 += '<input id="pageNum" type="hidden" value="'+pageNum+'">'
					if(data["startpage"] > 1){
						result2 += '<a href="javascript:void(0);" onclick="pageBlock('+data["pages"][0]+',0)"><span class="pageFont">···</span></a>&nbsp;&nbsp;'
					}
					$.each(data["pages"], function(index, page){
						if(page == data["pageNum"]){
							result2 += '<span class="pageFont"><b>['+page+']</b></span>&nbsp;&nbsp;'
						}else{
							result2 += '<a href="javascript:void(0);" onclick="pageBlock(this,2)"><span class="pageFont">'+page+'</a></span>&nbsp;&nbsp;'
						}
					})
					if(data["endpage"] < data["pagecount"]){
						result2 += '<a href="javascript:void(0);" onclick="pageBlock('+data["pages"][1]+',1)"><span class="pageFont">···</span></a>'
					}
					result2 += '</div>'
					$("#pageFor").html(result2)	
					
					if(data["pageNum"] == "1"){
						document.getElementById("lBtn").disabled = true;
					}else{
						document.getElementById("lBtn").disabled = false;
					}					
					if(data["pageNum"] == data["pagecount"]){
						console.log("pageNUm : 같댕");
						document.getElementById("rBtn").disabled = true;
					}else{
						document.getElementById("rBtn").disabled = false;
					}
				},
				error : function(request, status, error){
					//console.log("code = "+ request.status + " error = " + error); // 실패 시 처리
					//console.log("error")
				}
			}
		);
}



