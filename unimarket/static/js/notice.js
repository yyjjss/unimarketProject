$(function () {
  $(".notice-page").click(function () {
    $(this).css("border-bottom", "3px solid black");
    $(".event-page").css("border-bottom", "0");
    var page_value = 1;
    
    let param = {"page_value" : Number(page_value)}
    
    $.ajax({
    	url : "uniNotice",
    	type : "POST",
    	data : JSON.stringify(param),
		dataType : "json",
    		success : function(data){
//    			console.log(data)
    			var value = " ";
    			
    			$.each(data["dtos"],function(index, dto){
    				console.log(dto["noticeNo"]);
    				value +=	'<a href="uniNoticetempt?noticeNo=' + dto["noticeNo"] + '" class="page-reader">'
    				value +=	'<div class="image">'
    				if(dto["eventImg"]!=""){
        			value +=    '<img src="/media/' + dto["eventImg"] + '" />'
    				}else{
//    					value += 	'<img src=' + '"{% static' + "'images/market_logo_cut.png'" + '%}">'
//    					value += 	'<img src="{% static ' + "'/images/market_logo_cut.png'" + '%}">'
    					value += 	'<img src="../../static/images/market_logo_cut.png">'
    				}
    				value +=  	'</div>'
    				value +=  	'<div class="title">'
    				value +=    '<h3><strong>' + dto["noticeTitle"] + '</strong></h3>'
    				value +=  	'</div>'
    				value +=  	'<div class="summary">' + dto["noticeContent"] + '</div>'
    				value +=  	'<div class="info">공지사항</div></a>'
    				})
    				$("h1 > strong").html("공지사항")
    				$("section").html(value)	
    		}
    })
  });
});

$(function () {
  $(".event-page").click(function () {
    $(this).css("border-bottom", "3px solid black");
    $(".notice-page").css("border-bottom", "0");
    var page_value = 2;
    
    let param = {"page_value" : Number(page_value)}
    
    $.ajax({
    	url : "uniNotice",
    	type : "POST",
    	data : JSON.stringify(param),
		dataType : "json",
    		success : function(data){
//    			console.log(data)
    			var value = " ";
    			
    			$.each(data["dtos"],function(index, dto){
//    				console.log(dto);
    				value +=	'<a href="uniEventtempt?noticeNo=' + dto["noticeNo"] + '" class="page-reader">'
    				value +=	'<div class="image">'
    					
    				value +=    '<img src="/media/' + dto["eventImg"] + '" />'
    				value +=  	'</div>'
    				value +=  	'<div class="title">'
    				value +=    '<h3><strong>' + dto["noticeTitle"] + '</strong></h3>'
    				value +=  	'</div>'
    				value +=  	'<div class="summary">' + dto["noticeContent"] + '</div>'
    				value +=  	'<div class="info">이벤트</div></a>'
    				})
    				$("h1 > strong").html("이벤트")
    				$("section").html(value)	
    		}
    })
  });
});
