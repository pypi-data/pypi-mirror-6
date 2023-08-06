/**************************************************************/
/* Prepares the cv to be dynamically expandable/collapsible   */
/**************************************************************/
function pre_prepareList(list_name){
	$(list_name).find('li:has(ul)')
	.click( function(event) {
		if (this == event.target) {
		    $(this).toggleClass('expanded');
		    $(this).children('ul').toggle('medium');
			if ($(this).hasClass('expanded')){
				$(this).children('.clik_for_details').text('(less)');
			}
			else{
				$(this).children('.clik_for_details').text('(more)');
			}
		}
	})
	.addClass('collapsed')
	.children('ul').hide();
}

function prepare_list() {
    
	pre_prepareList('#runDetailsList');
	pre_prepareList('#runSummaryList');

	//Create the button funtionality
	$('#expandList')
	.unbind('click')
	.click( function() {
	$('.collapsed').addClass('expanded');
	$('.collapsed').children().show('medium');
	$('.collapsed').children('.clik_for_details').text('(less)');
	})

	$('#collapseList')
	.unbind('click')
	.click( function() {
	$('.collapsed').removeClass('expanded');
	$('.collapsed').children('ul').hide('medium');
	$('.collapsed').children('.clik_for_details').text('(more)');
	})
    
};
