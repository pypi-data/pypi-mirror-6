

  function deletefile(file){
	  
	  confirm_delete = confirm("Are you sure you want to delete this file?");
	  if(confirm_delete == false){
		  return;
	  }
	  myspinner.spin($("#spinner")[0]);
		$.ajax({
	         url: "/api/v1/files/" + file + "/",
	         type: "DELETE",
	         beforeSend: function(xhr, settings){
	        	 if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
	 	            // Send the token to same-origin, relative URLs only.
	 	            // Send the token only if the method warrants CSRF protection
	 	            // Using the CSRFToken value acquired earlier
	 	        	var csrftoken = $.cookie('csrftoken');
	 	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	 	        }
	        	 xhr.setRequestHeader('AppId', $app_object.key);
	        	 
	         },
	         success: function(data) {
	        	myspinner.stop();
	        	$scope.selectApp($app_object.name)
			  }
	      });
  }
  



