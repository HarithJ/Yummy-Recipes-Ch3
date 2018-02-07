function validateForm()
{
    var a=document.forms["regForm"]["name"].value;
    var b=document.forms["regForm"]["email"].value;
    var c=document.forms["regForm"]["password"].value;
    var d=document.forms["regForm"]["verpassword"].value;

    if (a==null || a=="", b==null || b=="", c==null || c=="", d==null || d=="")
    {
        alert("Please Fill All Required Field Marked With *");
        return false;
    }
}

/**
 * Takes one argument,
 * checks if the argument provided has any special characters,
 * or if it has leading spaces,
 * or if it contains nothing,
 * if any of the above is true, then it shall return false.
 */
function checkInputField(inputFieldText){
    let isOk = true;

    let re = /^[-,.()\/a-zA-Z0-9 ]*$/;
    isOk = re.test(inputFieldText);

    if (isOk == true){
        let re2 = /^\S/;
        isOk = re2.test(inputFieldText);
    }

    if (inputFieldText == ""){
        isOk = false
    }

    return isOk;
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
            let prevIngredient = $(this).parent().parent().find(`.ingredient${ing_num-1}`);

            if (checkInputField(prevIngredient.val()) == true){
                $("#ingredients #last-ingredient-list").before('<li><input class="validate ingredient' + ing_num + '" type="text" name="' + name+ing_num + '"><button type="button" class="close del-ingredient" aria-label="Delete Ingredient"><span aria-hidden="true">&times;</span></button></li>');
                $("#ingredients input[name=" + name+ing_num + "]").focus();
                ing_num += 1;
            }

        });
    }

    function deleteIngredient(ingredient){
        del_ing_num = ingredient.find("input").attr('class').match(/\d+/)[0];
        del_ing_num=parseInt(del_ing_num);

        update_ing_num = del_ing_num;


        ingredient.remove();

        while(update_ing_num < ing_num){
            let current_ing = $("#ingredients").find(`.ingredient${update_ing_num+1}`);
            current_ing.attr("name", `ingredient${update_ing_num}`);
            current_ing.removeClass(`ingredient${update_ing_num+1}`).addClass(`ingredient${update_ing_num}`);
            update_ing_num += 1;
        }

    }

    // when a user intends to rmv a ingredient
    $("#ingredients").on("click", ".del-ingredient", function(){
        deleteIngredient($(this).parent());
    });

    // When a user clicks on the edit btn for recipe
    $(".recipe .edit").on("click", function(){
        resetRecipeForm();
        prev_title = $(this).closest(".recipe").find(".recipetitle").text();

        $("#add-recipe-modal-form").attr("action", "/editrecipe/"+prev_title);

        // Add the recipe's title to the forms title input element
        $("#add-recipe-modal-form .recipetitle").val($(this).closest(".recipe").find(".recipetitle").text());

        // Add image name
        $("#add-recipe-modal-form input[name='hidden_recipe_image']").val($(this).closest(".recipe").find("img").attr('name'));
        $("#add-recipe-modal-form input[name='hidden_recipe_image']").attr("type", "text");

        // Add the recipe's ingredients to the forms ingredients list
        while ($(this).closest(".recipe").find(".ingredient"+ing_num).length){
            $("#ingredients #last-ingredient-list").before('<li><input class="ingredient' + ing_num + '" type="text" name="' + name+ing_num + '"><button type="button" class="close del-ingredient" aria-label="Delete Ingredient"><span aria-hidden="true">&times;</span></button></li>');
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




    $(".edit-category").on("click", function(){
        currentCategoryName = $(this).closest(".category").find(".category-name").text();

        var formForEditng = `<br/><div class="row justify-content-center category">
        <form method="Post" action="/editcategory/${currentCategoryName}" name="addcategoryForm">
            <input value="${currentCategoryName}" type="text" name="category_name"/>
            <button type="submit" class="btn btn-warning">Rename!</button>
        </form> </div>`;

        $(this).parent().parent().replaceWith(formForEditng);
    });


    /*
    When a form's submit button is clicked, then it will render the below function
    before submitting the form. This will check if the input provided by the user is ok or not
    by using the checkInputField function defined above this doc ready func.
    */
    $('form').submit(function(){
        if ( $( ".hidden-control" ).length ) {
            $(".hidden-control").attr("type", "text");
        }

        let submit = true;
        $('.validate').each(function(){
            let divError = `<div class="flex-wrap text-danger div-error">The above input is empty or contains illegal set of characters</div>`;
            if (checkInputField($(this).val()) == true){
                submit = true;
               $('.div-error').remove();
            }

            if (checkInputField($(this).val()) == false){
               submit = false;
               $(this).parent().append(divError);
            }
        });
        return submit;
    });
});