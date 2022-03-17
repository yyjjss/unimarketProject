$(document).ready(function(){
//	필터 탭 위 아래 이동
		$(".filter").on("click",move)
		function move(){
			var top = $(".filter-tab").css("top")
			if (top == "0px"){
				$(".filter-tab").css("display","flex");
				$(".filter-tab").css("top","40px");
			}else{
				$(".filter-tab").css("top","0px");
				$(".filter-tab").css("display","none");
			}
		}
//		프로필 탭(모달창) 좌우 이동
	  $(".profile").on("click", profileTab);
	  function profileTab() {
		$(".profileTab").show(1);
	    $(".profileTab").css("transform", "translateX(-300px)");
	    $(".blackbox").fadeIn(300);
	  }
	  $(".blackbox").on("click", exitProfile);
	  function exitProfile() {
		$(".profileTab").hide(301);
	    $(".profileTab").css("transform", "translateX(0px)");
	    $(".blackbox").fadeOut(300);
	  }
//	  카테고리 탭 좌우 이동
		$(".nav_category").on("click",category_move)
		function category_move(){
			var left = $(".category_list_home").css("left")
			if (left == "0px"){
			      $(".category_list").addClass("hidden"), $(".category_list_home").css("left", "-300px");
			}else{
			      $(".category_list").removeClass("hidden"), $(".category_list_home").css("left", "0");
			}
		}
//		사이드바 이전상품 보기 
		$("#side_open").on("click", sideOpen);
		function sideOpen() {
			$(".side_tab").show(1);
			$(".side_tab").css("transform", "translateX(-300px)")
		}
		$("#side_close").on("click", sideClose);
		function sideClose() {
			$(".side_tab").css("transform", "translateX(0px)");
			$(".side_tab").hide(300);
		}
	
})
//			검색어 자동완성 선택
$(document).on("click","#searchCP_box h4",function(){	
	if($(this).text().match("&nbsp")){
		return;
	}else{
		console.log($(this).text())
		$("input[name='kwrd']").val($(this).text())
	}
})


$("document").ready(function(){
	$.ajax({
    	url : "uniBase",
    	type : "POST",
    		success : function(data){
    			var alarm = "";
    			var count = 0;
    			
    			if(data["Ascount"] != 0){
    				
        			alarm += '<div class="list-group-item"> 이달의 공지 ' + data["Ascount"] + '건 </div>'
        			
    			}
    			if(data["Evcount"] != 0){
    				
        			alarm += '<div class="list-group-item"> 이달의 이벤트 ' + data["Evcount"] + '건 </div>'
        			
    			}
    			if(data["Recount"] != 0){
    				
        			alarm += '<div class="list-group-item"> 상품 신고 ' + data["Recount"] + '건 </div>'
        			
    			}
    			if(data["Secount"] != 0){
    				
        			alarm += '<div class="list-group-item"> 거래신청 ' + data["Secount"] + '건 </div>'
        			
    			}
				if(data["Itcount"] != 0){
					
					alarm += '<div class="list-group-item"> 게시후 일주일 경과 상품 ' + data["Itcount"] + '건 </div>'
					
				}
    			if(data["Alcount"] == 0) {
    				
    				alarm += '<div class="list-group-item">새로운 알람내역이 존재하지 않습니다.</div>'
    					
    			};
//    			
    			count += data["Alcount"]
    			
    			$(".alarm-box").html(alarm)
    			$(".icon > .badge").html(count)
    			console.log(data["Alcount"])
    			console.log(data["Ascount"])
    			console.log(data["Evcount"])
    			console.log(data["Recount"])
    			console.log(data["Secount"])
    			console.log(data["Itcount"])
    		}
    })
})

$(document).on("change",'input[name="reward"]',function(){
	console.log($('input[name="reward"]:checked').val())
		$.ajax(
				{
					url : "uniReward",
					type : "POST",
					data : {
						"reward" : $('input[name="reward"]:checked').val()
					},
					dataType : "text",
					success : function(data) {
						console.log(data)
						if(data == "판매자 닉네임") {
							$(".cat_filter").attr("href","myCat")
							$(".cat_filter span").text("전체")
							$("#category0").prop("checked", true)
							
						} else if(data == "제목" || data =="제목+내용" ) {
							$(".cat_filter").attr("href","#myCat")

						}
						$(".reward span").text(data)

						
					},
					error : function(){
						
					}
				}
			);
	});

$(document).on("change",'input[name="cat_filter"]',function(){
	console.log($('input[name="cat_filter"]:checked').val())
		$.ajax(
				{
					url : "uniCat",
					type : "POST",
					data : {
						"cat_filter" : $('input[name="cat_filter"]:checked').val()
					},
					dataType : "text",
					success : function(data) {
						console.log(data)
						$(".cat_filter span").text(data)
					},
					error : function(){
						
					}
				}
			);
	});

$(document).ready(function(){
	$("input[name='kwrd']").keydown(function(e){
		let kwrd = $('input[name="kwrd"]').val().trim()
		let reward = $('input[name="reward"]:checked').val()
		let cat = $('input[name="cat_filter"]:checked').val()
		if(e.key === ' '){
			$("#searchCP_box").css("display","block")
			var dict = {
							"search_ward" : kwrd,
							"search_reward" :reward,
							"search_cat" : cat
						}
			console.log(dict)
			$.ajax(
						{
						url : "uniSearch",
						type : "POST",
						data : JSON.stringify(dict),
						dataType : "json",
						success : function(data) {
							console.log(data)
							var searchCP = "";
							$.each(data["kt"],function(index, ktward){
								console.log(ktward)
								searchCP += "<h4>"+ktward+"</h4>"
							})
							if(data["kt"].length == 0){
								searchCP += "<h4> &nbsp&nbsp&nbsp 찾으신 '"+data["search_ward"]+"'(은)는</h4>"
								searchCP += "<h4> &nbsp&nbsp&nbsp 존재하지 않는</h4>"
								searchCP += "<h4> &nbsp&nbsp&nbsp 키워드 입니다.</h4>"
							}
							$("#searchCP > h4").remove()
							$("#searchCP").html(searchCP)
						},
						error: {
						}

						}
					);
			
		} else{
			$("#searchCP_box").css("display","none")
		}
	})
})

$("html").on("click",function(e){
	if(!$(e.target).is("#searchCP_box")){
		$("#searchCP_box").css("display","none")
	}
})
