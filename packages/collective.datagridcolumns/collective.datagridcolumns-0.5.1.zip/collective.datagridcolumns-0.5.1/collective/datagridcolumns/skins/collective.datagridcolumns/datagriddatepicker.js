/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jQuery: false, document: false, window: false */

/**
 * JavaScript for the DateColumn with calendar feature
 *
 * @author cekk
 */

(function($) {
    if (!window.DATAGRIDFIELD_DATE_ENABLED) {
        /*
         * This trick help us to run the autocomplete only once
         * (if we have more than one ReferenceColumn in a page
         */
        window.DATAGRIDFIELD_DATE_ENABLED = true;
        $(document).ready(function () {
            /**
             * The first time we get the focus, we will enable the date pickers
             */
            $('input.DataGridDatepicker').live('focus', function () {
                var $this = $(this);
                if (!$this.data('datepickerEnabled')) {
                    if (window.console && window.console.info) {
                        window.console.info('Datepicker enabled onto field');
                        window.console.log($this);
                    }
                    $this.data('datepickerEnabled', true);
                    $this.datepicker({ dateFormat: this.getAttribute('data-dateformat') });
                }
            });
        });
    }
})(jQuery);

