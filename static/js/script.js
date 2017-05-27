/*function submitUserResponse() {
	console.log("test");
	 console.log($('#taskId').val());
    		var taskId = $('#taskId').val();
    		var userResponse = $('#userResponse').val();
    		var sendInfo = {

                   };
            console.log(JSON.stringify(sendInfo));
    		$.ajax({
    			url: '/userUpdateTask',
    			contentType: "application/json; charset=utf-8",
    			data: JSON.stringify(sendInfo),
    			dataType: "json",
    			type: 'POST',
    			success: function(response){
    				alert(response)
    				console.log(response);
    			},
    			error: function(error){
    				console.log(error);
    			}
    		});
    	}
    	*/
 var wizardClickedFinish = false

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
          error: function(e) {
            console.log(e);
          },
          dataType: "json",
          contentType: "application/json",
          success: function(response){
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
          error: function(e) {
            console.log(e);
          },
          dataType: "json",
          contentType: "application/json",
          success: function(response){
          $("tr:has(td)").remove();

          // 2. get each article
          console.log(response)
          $.each(response, function (index, restaurant) {
              // 2.2 Create table column for categories
              var td_categories = $("<td/>");

              // 2.3 get each category of this article
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

          	$('#added-articles').append( '<tr>' + venueName + address + price + score + '</tr>')
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
        console.log(wizardClickedFinish)
 		var taskId = $('#taskId').text();
 		var wizardResponse = $('#wizardResponse').val();
 		var sysAct = $('#sysAct').val()
 		console.log(sysAct)
 		var end = $('#endOfDialogue').prop('checked')
		wizardClickedFinish = false
    	$.ajax({
          type: 'POST',
          url: "/wizardUpdateTask",
          data: JSON.stringify({
            "task_id": taskId,
            "wizard_response": wizardResponse,
            "sys_dia_act": sysAct,
            "end": end
          }),
          error: function(e) {
            alert(JSON.stringify(e))
            console.log(e)
          },
          dataType: "json",
          contentType: "application/json",
          success: function(response){
              				alert(JSON.stringify(response))
              				console.log(response);
              			}
        });
       };

  function validWizardClickedFinish() {
     if (wizardClickedFinish) {
     return true
     }
     return false
  }