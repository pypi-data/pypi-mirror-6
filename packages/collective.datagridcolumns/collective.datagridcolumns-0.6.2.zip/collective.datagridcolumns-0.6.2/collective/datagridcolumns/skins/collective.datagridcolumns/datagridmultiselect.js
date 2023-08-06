/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jQuery: false, document: false, window: false */

/**
 * JavaScript for the MultiSelectColumn
 * 
 * @author keul
 */

(function($) {
	$(document).ready(function () {
        /**
         * After a new DataGridField row has been created we need to fix the checkbox attached label,
         * as the new input "id" and the label "for" will have the same values of the model row
         */
		$(".datagridwidget-table-edit").delegate('tr.datagridwidget-row', "created.DataGridField", function(event) {
			$('.dataGridMultiSelectCell', this).each(function() {
				var $container = $(this),
					cb = $(':checkbox', $container),
					label = $('label', $container),
					name = cb.attr('name'),
					newId = name.replace('.', '_');
				cb.attr('id', newId);
				label.attr('for', newId);
			});
		});

	});
})(jQuery);

