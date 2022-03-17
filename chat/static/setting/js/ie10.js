if (navigator.userAgent.match(/IEMobile/\10/.0\)){
 var msViewportStyle = document.createElement("style");   

msViewportStyle.appendChild(document.createTextNode("@-ms-vieport{width:auto!important}"));

document.getElementsByTagName("head")
[0].appendChild(msViewportStyle);
}