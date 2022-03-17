$(document).ready(function(){
	$("#popup-box").fadeIn(300);
	$("#popup-box").css("transform","translateY(0px)");
})
$(document).ready(function(){
	$("form[name='popup'] button").on("click",function(){
		console.log($('input[type="checkbox"]:checked').val())
		$("#popup-box").css("transform","translateY(500px)");
		$("#popup-box").fadeOut(1000);
		if($('input[type="checkbox"]:checked').val() != undefined){
			setCookie("popup","1",3);
		}
	})
})

function setCookie(cookie_name, value, days) {
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + days);
	// 설정 일수만큼 현재시간에 만료값으로 지정

	var cookie_value = escape(value) + ((days == null) ? '' : '; expires=' + exdate.toUTCString());
	document.cookie = cookie_name + '=' + cookie_value;
}



// main-recet 좌우 버튼
$("document").ready(function () {
  $(".main-recent > .right-button").on("click", nextrecent);
  $(".main-recent > .left-button").on("click", prevrecent);
  function nextrecent() {
	  $(".recent-list").append($(".recent-list .recent-goods:first"));
  }
  function prevrecent() {
	  $(".recent-list").prepend($(".recent-list .recent-goods:last"));
  	}
});


//main-newest 좌우버튼

$("document").ready(function () {
  $(".main-newest > .right-button").on("click", nextnewest);
  $(".main-newest > .left-button").on("click", prevnewest);
  function nextnewest() {
	  $(".newest-list").append($(".newest-list .newest-goods:first"));
  }
  function prevnewest() {
	  $(".newest-list").prepend($(".newest-list .newest-goods:last"));
  }
});






