/**
 * Compound Index - archive behaviour.
 *
 * Only job: submit the sort form when the dropdown changes, so the control
 * works without a Go button. Everything else on the archive is plain links and
 * ordinary form submissions handled by WooCommerce.
 */
( function () {
	'use strict';

	document.addEventListener( 'DOMContentLoaded', function () {
		var root = document.querySelector( '.compound-index' );

		if ( ! root ) {
			return;
		}

		root.addEventListener( 'change', function ( event ) {
			var select = event.target;

			if ( ! select.matches || ! select.matches( '.ci-sort select' ) ) {
				return;
			}

			var form = select.closest( 'form' );

			if ( form ) {
				form.submit();
			}
		} );
	} );
}() );
