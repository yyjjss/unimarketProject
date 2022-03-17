$(function () {
  $("#input_img").on("change", function () {
    readURL(this);
    $("#img_container").css({ background: "white" });
    $("#img_container > strong").remove();
  });
});
function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function (e) {
      $("#preview").attr("src", e.target.result);
    };
    reader.readAsDataURL(input.files[0]);
  }
}
