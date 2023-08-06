/**
 * Scripts for collective.sortmyfolder
 */

(function($) {

$(document).ready(function() {
	var $page = $('#sortingUI');
	var $customCommand = $(':radio:last', $page);
	var $customCommandData = $('#choice_custom_data');
	var $customCommandField = $('#choice_custom_field');
	
	$customCommandField.show();
	$customCommand.removeAttr('disabled');
	
	var refresh = function() {
		if ($customCommand.is(':checked')) {
			$customCommandData.removeAttr('disabled');
		} else {
			$customCommandData.attr('disabled', 'disabled');
		}
	};

	$(':radio').click(refresh);
	
	$customCommandData.blur(function() {
		$customCommand.val($customCommandData.val());
	});
	
	refresh();
});
})(jQuery);
