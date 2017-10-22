function validateForm()
{
    var a=document.forms["regForm"]["name"].value;
    var b=document.forms["regForm"]["email"].value;
    var c=document.forms["regForm"]["password"].value;
    var d=document.forms["regForm"]["verpassword"].value;
    if (a==null || a=="",b==null || b=="",c==null || c=="",d==null || d=="")
    {
        alert("Please Fill All Required Field Marked With *");
        return false;
    }
}

$( document ).ready(function() {
    var numForName = 2;
    var name = "ingredient";


    $("#ingredients").on("focus","input", function(){

            $("#ingredients").append('<li><input type="text" name="' + name+numForName + '"></li>');
            numForName += 1;

    });

});