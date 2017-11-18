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
    let ing_num = 1;
    let name = "ingredient";

    function resetRecipeForm(){
        ing_num = 1;
        $("#add-recipe-modal form")[0].reset();
        $("#ingredients").empty();
        $("#ingredients").append( '<li id="last-ingredient-list"><input type="text" name="last-ingredient"></li>');
    }

    function addNewIng(){
        $("#ingredients input[name=last-ingredient]").on("focus", function(){

            $("#ingredients #last-ingredient-list").before('<li><input class="ingredient' + ing_num + '" type="text" name="' + name+ing_num + '"></li>');
            $("#ingredients input[name=" + name+ing_num + "]").focus();
            ing_num += 1;

        });
    }

    // When a user clicks on the edit btn
    $(".recipe .edit").on("click", function(){
        resetRecipeForm();
        prev_title = $(this).closest(".recipe").find(".recipetitle").text();
        console.log(prev_title);
        $("#add-recipe-modal-form").attr("action", "/editrecipe/"+prev_title);

        // Add the recipe's title to the forms title input element
        $("#add-recipe-modal-form .recipetitle").val($(this).closest(".recipe").find(".recipetitle").text());

        // Add the recipe's ingredients to the forms ingredients list
        while ($(this).closest(".recipe").find(".ingredient"+ing_num).length){
            $("#ingredients #last-ingredient-list").before('<li><input class="ingredient' + ing_num + '" type="text" name="' + name+ing_num + '"></li>');
            $("#add-recipe-modal-form .ingredient"+ing_num).val($(this).closest(".recipe").find(".ingredient"+ing_num).text());

            ing_num += 1;
        }

        //Add the recipe's directions to the forms directions text area
        $("#add-recipe-modal-form .directions").val($(this).closest(".recipe").find(".directions").text());

        addNewIng(); //give the user the ability to add a new ingredient
        $("#add-recipe-modal").modal("show");

    });

    // When a user clicks the delete recipe btn
    $(".delete-recipe").on("click", function(){
        $(".delete-recipe").attr("href", "/deleterecipe/"+$(this).closest(".recipe").find(".recipetitle").text());
    });

    // when a user intends to add new recipe
    $("#add-recipe").on("click", function(){
        resetRecipeForm();
        $("#add-recipe-modal-form").attr("action", "/addrecipe/");
        $("#add-recipe-modal").modal("show");

        addNewIng();
    });
});