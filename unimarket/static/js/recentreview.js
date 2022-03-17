
// uniDetail - 추천만족도 조사 페이지 열기 
//$(document).ready(function(){
//	$(".purCk").on(
//		"click", function(){
//			if($("#buyMemNo").val() == "None"){
//				alert("회원에게만 제공되는 기능입니다.");
//				return false;
//			}else{
//				let itemNo = $(".purCk").val();
//				let recommend = $("#recommend").val();
//				if(recommend==1){
//					url="uniRecentreview"+"?itemNo="+itemNo
//					open(url, "confirm", "toolbar=no, menubar=no, scrollbar=no, width=600, height=300");
//					return false;
//				}else{//recommend ==0
//					document.detailForm.submit();
//				}
//				
//			}
//		}
//	);
//});
function purCheck(){
	if($("#buyMemNo").val() == "None"){
		alert("회원에게만 제공되는 기능입니다.");
		return false;
	}else{
		let itemNo = $(".purCk").val();
		let recommend = $("#recommend").val();
		let recommendck = $("#recommendck").val();
		if(recommend==1){
			if(recommendck == 0){
				url="uniRecentreview"+"?itemNo="+itemNo
				open(url, "confirm", "toolbar=no, menubar=no, scrollbar=no, width=600, height=300");
				return false;
			}else{
				document.detailForm.submit();
			}
		}else{//recommend ==0
			document.detailForm.submit();
		}
	}
}


//uniRecentreview - 닫기 버튼 누를시 필수 만족도 조사임으로 닫기를 누르면  거래신청이 취소됨을 안내
$(document).ready(function(){
	$(".btn-close").mouseover(
		function(){
			$("#close-tooltip").attr("title","닫기를 누르면  거래신청이 취소됩니다");
		}
	);
	$(".btn-close").mouseout(
			function(){
				$("#close-tooltip").attr("title","");
		}
	);
	$(".btn-close").on(
		"click", function(){
			window.close();
		}
	);
});



// uniRecentreview - 전송버튼 클릭시 라디오 버튼을 선택했는지 여부 확인
function radioCk(){
	let check = $("input[name='recentreview']:checked").val();
	if(check){
		window.opener.name="uniDetail"; // 부모창 이름
		document.recentForm.target = "uniDetail"; // 적용될 페이지 부모창으로 설정
		document.recentForm.action = "updateRecentreview";
		document.recentForm.submit();
		self.close();
	}else{
		alert("만족도를 하나 선택해주세요.")
		return false;
	}
}

// uniDetail - 신고 페이지 열기 reportClick
$(document).ready(function(){
	$(".reportClick").on(
		"click", function(){
			if($("#reportck").val() == -1){
				alert("회원에게만 제공되는 기능입니다.");
			}else{
				if($("#sellMemNo").val() == $("#buyMemNo").val()){
					alert("회원님의 등록상품입니다.")
				}else{
					open("uniReport", "reportForm", "toolbar=no, menubar=no, scrollbar=no, width=600, height=600");
				}
			}
		}
	);
});

// uniReport - 닫기 버튼 누를시 신고작성 취소
$(document).ready(function(){
	$(".btn-reportClose").on(
		"click", function(){
			window.close();
		}
	);
});

// uniReport - 전송버튼 클릭시 글자수 확인하여 update
function reportContentCk(){
	let content = $("#reportContent").val();
	if(content.length >= 50){
		$.ajax(
				{
					url : "updateReport",
					type : "POST",
					data : {
						"reportFrom" : $("#reportFrom").val(),
						"reportTo" : $("#reportTo").val(),
						"reportContent" : $("#reportContent").val(),
						"itemNo" : $("#itemNo").val(),
					},
					dataType : "text",
					success : function(data){
						console.log(data);
						window.close();
						opener.$("#sirenC").show();
						opener.$("#sirenW").hide();
					},
					error : function(request, status, error){
						console.log("code = "+ request.status + " message = " + request.responseText + " error = " + error); // 실패 시 처리
						console.log("error")
					}
				}
			);
	}else{
		alert("50자 이상 작성해주세요");
		reportForm.reportContent.focus();
	}
}


//uniDetail - 찜 클릭할시 화면 reload없이 찜수 변경을 위해 ajax활용
function updateLikeCnt(){
	if($("#buyMemNo").val() == "None"){
		alert("회원에게만 제공되는 기능입니다.");
		return false;
	}else{
		$.ajax(
				{
					url : "updateLike",
					type : "POST",
					data : {
						"itemNo" : $("#btn-Like").val(),
						"price" : $("#hidden-price").val(),
					},
					dataType : "text",
					success : function(data){
						console.log(data);
						$("#span-like").html(data);
						if(data == 0){
							//alert("no");
							$("#noheart").show();
							$("#likeheart").hide();
						}else{
							//alert("like");
							$("#likeheart").show();
							$("#noheart").hide();
						}
						
					},
					error : function(request, status, error){
						console.log("code = "+ request.status + " message = " + request.responseText + " error = " + error); // 실패 시 처리
						console.log("error")
					}
					
				}
			);
	}
	
}
