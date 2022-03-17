// 전체 체크 
function registerck() {
	if (!checkUserId(registerform.email.value)) {
		return false;
	}
	if (!checkPassword(registerform.email.value, registerform.passwd.value,
			registerform.passwd1.value)) {
		return false;
	}
	if (!checkName(registerform.nickname.value)) {
		return false;
	}
	if (!checkBdate(registerform.bDate.value)) {
		return false;
	}
	if (!checkLocation(registerform.location.value)) {
		return false;
	}

	return true;
}

// 이메일 중복체크
function dupChk(){
	email = document.getElementById("email").value;
	console.log("email : "+email);
	var data = {"user_email" : email,}
	$.ajax({
		url : "uniEmailChk",
		type : "POST",
		data : data,
		dataType : "text",
		success : function(data){
			console.log("success");
			console.log(data);
			//location.href=data;
			window.open(data, "이메일중복체크", height="500px", width="300px");
		},
		error : function(request, status, error){
			//console.log("code = "+ request.status + " error = " + error); // 실패 시 처리
			console.log("error")
		}
	});
}

function setid(user_email) {
	opener.document.registerform.user_email.value = user_email
	opener.document.registerform.uniEmailChk.value = 1;
	window.close()
}

// 공백확인 함수
function checkExistData(value, dataName) {
	if (value == "") {
		alert(dataName + " 입력해주세요.");
		return false;
	}
	return true;
}

function checkUserId(email) {
	//email이 입력되었는지 확인하기
	if (!checkExistData(email, "이메일을"))
		return false;

	var emailRegExp = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/;
	if (!emailRegExp.test(email)) {
		alert("이메일 형식이 올바르지 않습니다.");
		registerform.email.value = "";
		registerform.email.focus();
		return false;
	}
	return true; //확인이 완료되었을 때
}

// 아이디, 비밀번호 다르게 
function checkPassword(email, passwd, passwd1) {
	//비밀번호가 입력되었는지 확인하기
	if (!checkExistData(passwd, "비밀번호를"))
		return false;
	//비밀번호 확인이 입력되었는지 확인하기
	if (!checkExistData(passwd1, "비밀번호 확인을"))
		return false;

	var passwdRegExp = /(?=.*\d)(?=.*[a-zA-ZS])(?=.*?[#?!@$%^&*-]).{8,24}/; //비밀번호 유효성 검사
	if (!passwdRegExp.test(passwd)) {
		alert("비밀번호는 문자,숫자,특수문자[#?!@$%^&*-] 조합의 8~24 자리로 입력해야합니다!");
		registerform.passwd.value = "";
		registerform.passwd.focus();
		return false;
	}
	//비밀번호와 비밀번호 확인이 맞지 않다면..
	if (passwd != passwd1) {
		alert("비밀번호가 일치하지 않습니다.");
		registerform.passwd.value = "";
		registerform.passwd1.value = "";
		registerform.passwd.focus();
		return false;
	}

	//아이디와 비밀번호가 같을 때..
	if (email == passwd1) {
		alert("아이디와 비밀번호는 같을 수 없습니다!");
		registerform.passwd.value = "";
		registerform.passwd1.value = "";
		registerform.passwd1.focus();
		return false;
	}
	return true; //확인이 완료되었을 때
}

//닉네임 입력 유무 파악
function checkName(nickname) {
	if (!checkExistData(nickname, "닉네임을"))
		return false;

	var nicknameRegExp = /^[가-힣a-zA-Z]+$/;
	if (!nicknameRegExp.test(nickname)) {
		alert("닉네임이 올바르지 않습니다.");
		return false;
	}
	return true; //확인이 완료되었을 때
}

//생년월일 유효성 체크
function checkBdate(bDate) {

	if (!checkExistData(bDate, "생년월일을"))
		return false;

	var year = ""
	var month = ""
	var day = ""
	var today = new Date(); // 날자 변수 선언
	var yearNow = today.getFullYear();
	var adultYear = yearNow - 13;

	if (bDate.value.length != 11) {
		console.log("hi: " + bDate.value.length);

		var birthDate = "";
		var w = true;
		if (bDate.value.length < 4) {
			console.log("1번 : 들어옴");
			return bDate;
		} else if (3 < bDate.value.length && bDate.value.length < 6) { // year 완성
			year = Number(bDate.value.substr(0, 4));
			console.log("2번 : 들어옴 : year : " + year);
			if (year < 1900 || year > adultYear) {
				bDate.value = "";
				alert("년도를 확인하세요. " + adultYear + "년생 이전 출생자만 등록 가능합니다.");
				return false;
			} else {
				birthDate += bDate.value.substr(0, 4);
				birthDate += "-";
				bDate.value = birthDate;
				console.log("요기2 : "+bDate.value.length);
				return bDate;
			}
		} else if (5 < bDate.value.length && bDate.value.length < 7) {
			console.log("3번이란다: "+bDate.value.length);
			return bDate;

		} else if (6 < bDate.value.length && bDate.value.length < 8) {// month 완성
			year = Number(bDate.value.substr(0, 4));
			month = Number(bDate.value.substr(5, 2));
			console.log("4번 : 들어옴: month : " + year + "-" + month);
			if (month < parseInt(01) || month > 12) {
				bDate.value = year + "-";
				alert("달은 1월부터 12월까지 입력 가능합니다.");
				return false;
			} else {
				birthDate += bDate.value.substr(0, 4);
				birthDate += "-";
				birthDate += bDate.value.substr(5, 2);
				birthDate += "-";
				bDate.value = birthDate;
				console.log("5번 : "+bDate.value.length);
				return bDate;
			}
		} else if (8 < bDate.value.length && bDate.value.length < 10) {
			console.log("6번 : "+bDate.value.length);
			return bDate
			
		} else if(9 < bDate.value.length && bDate.value.length < 11){
			year = Number(bDate.value.substr(0, 4));
			month = bDate.value.substr(5, 2);
			day = Number(bDate.value.substr(8, 2));
			console.log("마지막: "+year+"-"+month+"-"+day);
			if (day < parseInt(01) || day > 31) {
				console.log("7번 : 들어옴: day 체크 : "+day)
				bDate.value = year + "-" + month + "-";
				alert("일은 1일부터 31일까지 입력가능합니다.");
				return false;
			}
			if ((Number(month) == parseInt(04) || Number(month) == parseInt(06)|| Number(month) == parseInt(09) || Number(month) == 11)
					&& day == 31) {
				bDate.value = year + "-" + month + "-";
				console.log("8번 : 들어옴: day 체크 : "+day)
				alert(month + "월은 31일이 존재하지 않습니다.");
				return false;
			}
			if (month == parseInt(02)) {
				year = Number(bDate.value.substr(0, 4));
				month = bDate.value.substr(5, 2);
				var isleap = (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0));
				if (day > 29 || (day == 29 && !isleap)) {
					
					bDate.value = year + "-" + month + "-";
					console.log("9번 : 들어옴: day 체크 : "+day)
					alert(year + "년 2월은  " + day + "일이 없습니다.");
					return false;
				}
			}
			birthDate += bDate.value.substr(0, 4);
			birthDate += "-";
			birthDate += bDate.value.substr(5, 2);
			birthDate += "-";
			birthDate += bDate.value.substr(8, 2);
			bDate.value = birthDate;
			return bDate;
		}
	}
	var bDateRegExp = /^[0-9](?=.*?[-]).{0,10}$/;
	//var bDateRegExp = /^(19[0-9][0-9]|20\d{2})-(0[0-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$/;
	if (!bDateRegExp.test(bDate.value)) {
		alert("생년월일이 올바르지 않습니다.");
		return false;
	} else {
		return true;
	}
}

	

//우리동네 입력 유무 파악
function checkLocation(location) {
	if (!checkExistData(location, "동네명을"))
		return false;
	return true;
}