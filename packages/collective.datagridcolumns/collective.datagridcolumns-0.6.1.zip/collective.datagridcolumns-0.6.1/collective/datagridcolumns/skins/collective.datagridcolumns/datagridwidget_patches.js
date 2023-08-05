/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jQuery: false, document: false, window: false */

/**
 * Some JavaScript hack to DataGridField limitations
 * 
 * @author keul
 */

(function($) {
	$(document).ready(function () {
        /**
         * We need to hack DataGridField "Add New Row" button, to raise an event after every add
         * The used trick is to add a new function call afther the default onclick
         */
		if (typeof(dataGridFieldFunctions.notifyNewRowAdded)==='undefined') {

			/**
			 * Notify a "created" event on the new row 
			 */
			dataGridFieldFunctions.notifyNewRowAdded = function(addbutton) {
				var $row = $(addbutton).parents('.ArchetypesDataGridWidget').find('tr.datagridwidget-row:last');
				$row.trigger('created.DataGridField');				
			}

			$('.datagridwidget-add-button').each(function() {
				// Backing up old function inline in HTML
				var onclickOldFun = this.onclick;
				// Clearing old function inline in HTML
				this.onclick = null;
				// Re-adding old function in morern way
				$(this).click(onclickOldFun);
				// Adding out code
				$(this).click(function(){dataGridFieldFunctions.notifyNewRowAdded(this)});
			});
			
		}

	});
})(jQuery);

