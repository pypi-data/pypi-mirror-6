/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jQuery: false, document: false, window: false */

/**
 * JavaScript for the DateColumn with calendar feature
 *
 * @author cekk
 */

(function($) {
    $(document).ready(function () {
        /**
         * The first time we get the focus, we will enable the date pickers
         */
		$(".datagridwidget-table-edit").delegate("input.DataGridDatepicker", "focus", function(event) {
            var $this = $(this);
            if (!$this.data('datepickerEnabled')) {
                if (window.console && window.console.info) {
                    window.console.info('Datepicker enabled onto following field:');
                    window.console.info($this);
                }
                $this.data('datepickerEnabled', true);
                $this.datepicker({ dateFormat: this.getAttribute('data-dateformat') });
            }
        });
    });
})(jQuery);

