function validateForm()
{
    var a=document.forms["regForm"]["name"].value;
    var b=document.forms["regForm"]["email"].value;
    var c=document.forms["regForm"]["password"].value;
    var d=document.forms["regForm"]["verpassword"].value;
    if (a==null || a=="",b==null || b=="",c==null || c=="",d==null || d=="")
    {
        document.getElementById("error").innerHTML = "Please Fill All Required Field";
        return false;
    }
}