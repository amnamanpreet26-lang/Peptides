<?php
/**
 * Plugin Name:       Compound Index - WooCommerce Archive Layout
 * Description:       Replaces the WooCommerce shop and product-category archives with the Compound Index layout: a stats header, category filter chips with live counts, and data-led product cards. Products always come from WooCommerce.
 * Version:           1.0.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Text Domain:       compound-index
 * Domain Path:       /languages
 * WC requires at least: 7.0
 * WC tested up to:   9.9
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

define( 'COMPOUND_INDEX_VERSION', '1.0.0' );
define( 'COMPOUND_INDEX_FILE', __FILE__ );
define( 'COMPOUND_INDEX_PATH', plugin_dir_path( __FILE__ ) );
define( 'COMPOUND_INDEX_URL', plugin_dir_url( __FILE__ ) );

require_once COMPOUND_INDEX_PATH . 'includes/settings.php';
require_once COMPOUND_INDEX_PATH . 'includes/stats.php';
require_once COMPOUND_INDEX_PATH . 'includes/product-meta.php';
require_once COMPOUND_INDEX_PATH . 'includes/template.php';

/**
 * Load a template part, letting the active theme override it.
 *
 * Drop a copy in your theme at compound-index/<name>.php to take control of any
 * part without touching the plugin.
 *
 * @param string $name Part name, relative to the plugin's templates directory.
 * @param array  $args Variables made available to the part.
 */
function compound_index_part( $name, array $args = array() ) {
	$override = locate_template( array( 'compound-index/' . $name . '.php' ) );
	$file     = $override ? $override : COMPOUND_INDEX_PATH . 'templates/' . $name . '.php';

	/**
	 * Filters the resolved path of a Compound Index template part.
	 *
	 * @param string $file The file about to be loaded.
	 * @param string $name The requested part name.
	 */
	$file = apply_filters( 'compound_index_template_part', $file, $name );

	if ( is_readable( $file ) ) {
		// phpcs:ignore WordPress.PHP.DontExtract.extract_extract -- deliberate, mirrors wc_get_template().
		extract( $args, EXTR_SKIP );
		include $file;
	}
}

add_action(
	'plugins_loaded',
	function () {
		if ( ! class_exists( 'WooCommerce' ) ) {
			add_action(
				'admin_notices',
				function () {
					echo '<div class="notice notice-error"><p>';
					esc_html_e( 'Compound Index needs WooCommerce to be installed and active.', 'compound-index' );
					echo '</p></div>';
				}
			);
			return;
		}

		Compound_Index_Settings::init();
		Compound_Index_Product_Meta::init();
		Compound_Index_Template::init();
	}
);

// Declare compatibility with WooCommerce High-Performance Order Storage.
add_action(
	'before_woocommerce_init',
	function () {
		if ( class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
			\Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'custom_order_tables', COMPOUND_INDEX_FILE, true );
		}
	}
);

register_deactivation_hook( COMPOUND_INDEX_FILE, array( 'Compound_Index_Stats', 'flush_cache' ) );
