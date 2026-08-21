<?php
/**
 * Compound Index - product archive layout for Avanam.
 *
 * Adds header fields to product categories and renders the shop and category
 * archives in the Compound Index design. The product loop is untouched: it stays
 * WooCommerce's own main query, so products, prices and stock all behave exactly
 * as WooCommerce intends.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

define( 'AVANAM_CI_DIR', get_template_directory() . '/inc/compound-index/' );
define( 'AVANAM_CI_URL', get_template_directory_uri() . '/' );

require_once AVANAM_CI_DIR . 'category-fields.php';
require_once AVANAM_CI_DIR . 'settings.php';
require_once AVANAM_CI_DIR . 'archive.php';

/**
 * Load one of the layout's template parts.
 *
 * A child theme can override any of them by placing a file of the same name in
 * its own compound-index/ directory.
 *
 * @param string $name Part name, without the .php extension.
 */
function avanam_ci_part( $name ) {
	$override = locate_template( array( 'compound-index/' . $name . '.php' ) );
	$file     = $override ? $override : AVANAM_CI_DIR . 'parts/' . $name . '.php';

	if ( is_readable( $file ) ) {
		include $file;
	}
}
