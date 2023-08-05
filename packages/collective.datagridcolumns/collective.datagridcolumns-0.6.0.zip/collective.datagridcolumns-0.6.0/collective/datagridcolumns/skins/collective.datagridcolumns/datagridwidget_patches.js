/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jQuery: false, document: false, window: false */

/**
 * Some JavaScript hack for DataGridField limitations
 * 
 * @author keul
 */

(function($) {
	$(document).ready(function () {
        /**
         * We need to hack DataGridField "Add New Row" button, to raise an event after every add
         * The used trick is to add a new function call afther the default onclick
         */
		if (dataGridFieldFunctions.notifyNewRowAdded!=='undefined') {

			// First: attach the function call to datagrid add button
			$('.datagridwidget-add-button').each(function() {
				$(this).attr('onclick', $(this).attr('onclick') + ';dataGridFieldFunctions.notifyNewRowAdded(this)');
			});
			
			/**
			 * Notify a "created" event on the new row 
			 */
			dataGridFieldFunctions.notifyNewRowAdded = function(addbutton) {
				var $row = $(addbutton).parents('.ArchetypesDataGridWidget').find('tr.datagridwidget-row:last');
				$row.trigger('created.DataGridField');				
			}
		}

	});
})(jQuery);

