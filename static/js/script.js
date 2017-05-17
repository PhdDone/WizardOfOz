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
 function submitUserResponse() {
 		var taskId = $('#taskId').text();
 		var userResponse = $('#userResponse').val();
    	$.ajax({
          type: 'POST',
          url: "/userUpdateTask",
          data: JSON.stringify({
            "taskId": taskId,
            "userResponse": userResponse,
            "sampleSize" : 10
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
 console.log("test")

     // JSON Data
var articles = [
    {
        "venue":"Cheng Du Xiao che",
        "address":"Zhong guan cun",
        "phone":["110"],
        "tags":["jquery","json","$.each"]
    },
    {
        "venue":"Sha Xian xiao chi",
        "address": "da heng",
    }
];
// 1. remove all existing rows
$("tr:has(td)").remove();

// 2. get each article
$.each(articles, function (index, article) {

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
    $.each(article.tags, function (i, tag) {
        var span = $("<span/>");
        span.text(tag);
        td_tags.append(span);
    });
    var venueName = '<td> ' + article.venue + '</td>'
    var address = '<td> ' + article.address + '</td>'
	$('#added-articles').append( '<tr>' + venueName + address + '</tr>')
    // 2.6 Create a new row and append 3 columns (title+url, categories, tags)
    /*$("#added-articles").append($('<tr/>')
            .append($('<td/>').html("<a href='"+article.url+"'>"+article.title+"</a>"))
            .append(td_categories)
            .append(td_tags)
    );*/
});
}