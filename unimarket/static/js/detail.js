// uniDetail - 가격에 콤마(,) 붙이기
$(document).ready(function(){
	var price = document.getElementById("price").value
    reprice = price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
	document.getElementById("price").value = reprice+" 원";
});

// uniDetail - 추천상품 슬라이드
$("document").ready(function () {
  $(".right-button").on("click", nextpage);
  $(".left-button").on("click", prevpage);
});

function nextpage() {
  $(".recent-list").append($(".recent-list div:first"));
}

function prevpage() {
  $(".recent-list").prepend($(".recent-list div:last"));
}

