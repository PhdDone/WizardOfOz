

function submitUserResponse() {
    var taskId = $('#taskId').text();
    var userResponse = $('#userResponse').val();
    var end = $('#endOfDialogue').prop('checked');
    console.log(end)
    $.ajax({
        type: 'POST',
        url: "/userUpdateTask",
        data: JSON.stringify({
            "task_id": taskId,
            "user_response": userResponse,
            "end": end
        }),
        error: function (e) {
            console.log(e);
        },
        dataType: "json",
        contentType: "application/json",
        success: function (response) {
            alert(JSON.stringify(response))
            console.log(response);
        }
    });
};

function searchDB() {
    wizardClickedFinish = true
    console.log("searchdb")
    console.log(wizardClickedFinish)
    var taskId = $('#taskId').text();
    var name = $('#name').val();
    var area = $('#area').val();
    var foodType = $('#foodType').val();
    var lowerBound = $('#priceRangeLowerBound').val();
    var upperBound = $('#priceRangeUpperBound').val();

    var askArea = $('#askArea').prop('checked')
    var askFoodType = $('#askFoodType').prop('checked')
    var askPrice = $('#askPrice').prop('checked')
    var askScore = $('#askScore').prop('checked')

    console.log(area)
    console.log(foodType)
    console.log(askArea)

    $.ajax({
        type: 'POST',
        url: "/searchDB",
        data: JSON.stringify({
            "task_id": taskId,
            "name": name,
            "area": area,
            "food_type": foodType,
            "lower_bound": lowerBound,
            "upper_bound": upperBound,
            "ds_asking_area": askArea,
            "ds_asking_food_type": askFoodType,
            "ds_asking_price": askPrice,
            "ds_asking_score": askScore
        }),
        error: function (e) {
            console.log(e);
        },
        dataType: "json",
        contentType: "application/json",
        success: function (response) {
            $("tr:has(td)").remove();

            // 2. get each res
            console.log(response)
            //sort response by score
            $.each(response, function (index, restaurant) {
                // 2.2 Create table column for categories
                var td_categories = $("<td/>");

                // 2.3 get each category of this restaurant
                /*$.each(article.categories, function (i, category) {
                 var span = $("<span/>");
                 span.text(category);
                 td_categories.append(span);
                 });*/

                // 2.4 Create table column for tags
                var td_tags = $("<td/>");

                // 2.5 get each tag of this article
                $.each(response.tags, function (i, tag) {
                    var span = $("<span/>");
                    span.text(tag);
                    td_tags.append(span);
                });
                var venueName = '<td> ' + restaurant.name + '</td>'
                var address = '<td> ' + restaurant.address + '</td>'
                var price = '<td>' + restaurant.price + '</td>'
                var score = '<td>' + restaurant.score + '</td>'
                var area = '<td>' + restaurant.area_name + '</td>'
                var foodType = '<td>' + restaurant.food_type + '</td>'

                $('#added-articles').append('<tr>' + venueName + address + score + price + area + foodType + '</tr>')
                // 2.6 Create a new row and append 3 columns (title+url, categories, tags)
                /*$("#added-articles").append($('<tr/>')
                 .append($('<td/>').html("<a href='"+article.url+"'>"+article.title+"</a>"))
                 .append(td_categories)
                 .append(td_tags)
                 );*/
            });

        }
    });
};

function submitWizardResponse() {
    var taskId = $('#taskId').text();
    var wizardResponse = $('#wizardResponse').val();
    var sysAct = $('#sysAct').val()
    console.log(sysAct)
    var end = $('#endOfDialogue').prop('checked')


    var sysSlotNames = $(".sysSlotName").map(function () {
        return $(this).val();
    }).get();

    var sysSlotValues = $(".sysSlotValue").map(function () {
        return $(this).val();
    }).get();

    console.log("end: " + end)

    var allSlots = []
    for (var i = 0; i < 10; ++i) {
        console.log("counter:" + i)
        var x = $('#diaact-' + i)

        if ( x.length === 0){
            break
        }
        console.log(x)
        var sysSlotNames = $('#diaact-' + i).find('.sysSlotName').map(function () {
            return $(this).val();
        }).get();

        var sysSlotValues = $('#diaact-' + i).find('.sysSlotValue').map(function () {
            return $(this).val();
        }).get();
        console.log(i)
        console.log(sysSlotNames)
        console.log(sysSlotValues)
        var slotInfo = {}

        for (var i = 0; i < sysSlotNames.length; ++i) {
            var name = sysSlotNames[i]
            if (name.includes("-")) {
                continue
            }
            var slotName = name.split(" ")[1]
            var slotValue = sysSlotValues[i]
            if (!slotValue) {
                slotValue = "UNK"
            }
            slotInfo[slotName] = slotValue
            console.log(slotInfo)
        }
        allSlots.push(slotInfo)
    }

    for (var i = 0; i < allSlots.length; ++i)
        console.log(allSlots[i])

    $.ajax({
        type: 'POST',
        url: "/wizardUpdateTask",
        data: JSON.stringify({
            "task_id": taskId,
            "wizard_response": wizardResponse,
            "sys_dia_act": sysAct,
            "end": end,
            "sys_slot_info": allSlots
        }),
        error: function (e) {
            alert(JSON.stringify(e))
            console.log(e)
        },
        dataType: "json",
        contentType: "application/json",
        success: function (response) {
            alert(JSON.stringify(response))
            console.log(response);
        }
    });
};

$(document).ready(function() {
    var buttonadd = '<span><button class="btn btn-success btn-add" type="button"><span class="glyphicon glyphicon-plus"></span></button></span>';
    var fvrhtmlclone = '<div class="fvrclonned">' + $(".fvrduplicate").html() + buttonadd + '</div>';
    $(".fvrduplicate").html(fvrhtmlclone);
    $(".fvrduplicate").after('<div class="fvrclone"></div>');

    var baseHtml = $("#diaact-0").html()
    var counter = 1

    $(document).on('click', '.btn-add', function (e) {
        if ($(this).hasClass('btn-add-2')){
            console.log("2")
        } else {
            //e.preventDefault();
            console.log($(this).parent().parent())
            $(this).parent().parent().parent().append(fvrhtmlclone)
            $(this).removeClass('btn-add').addClass('btn-remove')
                .removeClass('btn-success').addClass('btn-danger')
                .html('<span class="glyphicon glyphicon-minus"></span>');
        }
    }).on('click', '.btn-remove', function (e) {
        $(this).parents('.fvrclonned').remove();
        //e.preventDefault();
        counter--
        //return false;
    });

    $("#AddDiaact").click(function () {
        console.log("addnewact")
        if (counter > 10) {
            alert("Only 10 textboxes allow");
            return false;
        }

        var newDiaactDiv = "<div class='form-group form-inline dup' id='diaact-" + counter + "'>" + baseHtml + "</div>"

        //var newTextBoxDiv = $(document.createElement('div'))
         //   .attr("id", 'TextBoxDiv' + counter);

        //newTextBoxDiv.after().html('<label>Textbox #' + counter + ' : </label>' +
        //    '<input type="text" name="textbox' + counter +
        //    '" id="textbox' + counter + '" value="" >');

        //newTextBoxDiv.appendTo("#TextBoxesGroup");
        $('.diaact').append(newDiaactDiv)

        counter++;
    });

    $("#RemoveDiaact").click(function () {
        if (counter == 0) {
            alert("No more dialogue act to remove");
            return false;
        }

        console.log(counter)
        counter--;
        $("#diaact-" + counter).remove();

    });

    $("#wizardSubmit").submit(function () {
        console.log("%%%")
        submitWizardResponse()
    })
    $("#getButtonValue").click(function () {

        for (var i = 0; i < counter; ++i) {
            var x = $('#diaact-' + i)
            console.log(x)
            var sysSlotNames = $('#diaact-' + i).find('.sysSlotName').map(function () {
                return $(this).val();
            }).get();

            var sysSlotValues = $('#diaact-' + i).find('.sysSlotValue').map(function () {
                return $(this).val();
            }).get();
            console.log(i)
            console.log(sysSlotNames)
            console.log(sysSlotValues)
        }


        var msg = '';
        for (i = 1; i < counter; i++) {
            msg += "\n Textbox #" + i + " : " + $('#textbox' + i).val();
        }
        alert(msg);
    });
});


function showValues() {
    var fields = $( ":input" ).serializeArray();
    $( "#results" ).empty();
    jQuery.each( fields, function( i, field ) {
        $( "#results" ).append( field.value + " " );
    });
}

function test() {
    var sysSlotNames = $(".sysSlotName").map(function () {
        return $(this).val();
    }).get();

    var sysSlotValues = $(".sysSlotValue").map(function () {
        return $(this).val();
    }).get();
    console.log(sysSlotNames)
    console.log(sysSlotValues)
}