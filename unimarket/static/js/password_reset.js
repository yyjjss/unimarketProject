// 전체 체크 
function password_reset_ck() {
	if (!checkPassword(password_resetform.passwd.value, password_resetform.passwd1.value)) {
		return false;
	}
	return true;
}

//아이디, 비밀번호 다르게 
function checkPassword(passwd, passwd1) {
	//비밀번호가 입력되었는지 확인하기
	if (!checkExistData(passwd, "비밀번호를"))
		return false;
	//비밀번호 확인이 입력되었는지 확인하기
	if (!checkExistData(passwd1, "비밀번호 재입력을"))
		return false;

	var passwdRegExp = /(?=.*\d)(?=.*[a-zA-ZS])(?=.*?[#?!@$%^&*-]).{8,24}/; //비밀번호 유효성 검사
	if (!passwdRegExp.test(passwd)) {
		alert("비밀번호는 문자,숫자,특수문자[#?!@$%^&*-] 조합의 8~24 자리로 입력해야합니다!");
		password_resetform.passwd.value = "";
		password_resetform.passwd1.value = "";
		password_resetform.passwd.focus();
		return false;
	}
	//비밀번호와 비밀번호 확인이 맞지 않다면..
	if (passwd != passwd1) {
		alert("비밀번호가 일치하지 않습니다.");
		password_resetform.passwd.value = "";
		password_resetform.passwd1.value = "";
		password_resetform.passwd.focus();
		return false;
	}
	return true;
}
//	//아이디와 비밀번호가 같을 때..
//	if (email == passwd1) {
//		alert("아이디와 비밀번호는 같을 수 없습니다!");
//		password_resetform.passwd.value = "";
//		password_resetform.passwd1.value = "";
//		password_resetform.passwd1.focus();
//		return false;
//	}
//	return true; //확인이 완료되었을 때
//}

// 공백확인 함수
function checkExistData(value, dataName) {
	if (value == "") {
		alert(dataName + " 입력해주세요.");
		return false;
	}
	return true;
}
