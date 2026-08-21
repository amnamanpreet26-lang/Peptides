<?php
/**
 * Render the Compound Index archive templates outside WordPress.
 *
 * Verification tool, not part of the deliverable. It stubs the WordPress and
 * WooCommerce functions the templates call, feeds them sample products, and
 * writes build/archive-preview.html so the result can be screenshotted and
 * compared against the reference design.
 *
 * Usage: php build/preview_archive.php
 *
 * phpcs:disable
 */

define( 'ABSPATH', __DIR__ );
define( 'HOUR_IN_SECONDS', 3600 );
define( 'EXTR_SKIP_COMPAT', true );

// --- state ------------------------------------------------------------------
$GLOBALS['ci_options']  = array();
$GLOBALS['ci_filters']  = array();
$GLOBALS['ci_index']    = -1;
$GLOBALS['ci_products'] = array();

// --- escaping / i18n --------------------------------------------------------
function esc_html( $t ) { return htmlspecialchars( (string) $t, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $t ) { return esc_html( $t ); }
function esc_url( $t ) { return esc_html( $t ); }
function esc_url_raw( $t ) { return $t; }
function esc_textarea( $t ) { return esc_html( $t ); }
function __( $t, $d = '' ) { return $t; }
function _e( $t, $d = '' ) { echo $t; }
function esc_html__( $t, $d = '' ) { return esc_html( $t ); }
function esc_html_e( $t, $d = '' ) { echo esc_html( $t ); }
function esc_attr_e( $t, $d = '' ) { echo esc_attr( $t ); }
function esc_attr__( $t, $d = '' ) { return esc_attr( $t ); }
function wp_kses_post( $t ) { return $t; }
function wp_strip_all_tags( $t ) { return strip_tags( (string) $t ); }
function wp_unslash( $t ) { return $t; }
function sanitize_text_field( $t ) { return trim( strip_tags( (string) $t ) ); }
function sanitize_key( $t ) { return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( (string) $t ) ); }
function wpautop( $t ) { return '<p>' . str_replace( "\n\n", '</p><p>', trim( (string) $t ) ) . '</p>'; }
function number_format_i18n( $n, $d = 0 ) { return number_format( (float) $n, (int) $d ); }
function absint( $n ) { return abs( (int) $n ); }
function wp_parse_args( $args, $defaults = array() ) { return array_merge( $defaults, (array) $args ); }
function is_wp_error( $t ) { return false; }
function selected( $a, $b = true, $echo = true ) { $r = ( (string) $a === (string) $b ) ? ' selected' : ''; if ( $echo ) { echo $r; } return $r; }
function checked( $a, $b = true, $echo = true ) { $r = ( (string) $a === (string) $b ) ? ' checked' : ''; if ( $echo ) { echo $r; } return $r; }

// --- hooks ------------------------------------------------------------------
function add_action( $h, $c, $p = 10, $a = 1 ) {}
function remove_action( $h, $c, $p = 10 ) {}
function do_action( $h, ...$args ) {}
function add_filter( $h, $c, $p = 10, $a = 1 ) { $GLOBALS['ci_filters'][ $h ][] = $c; }
function apply_filters( $h, $value, ...$args ) {
	foreach ( $GLOBALS['ci_filters'][ $h ] ?? array() as $cb ) {
		$value = call_user_func_array( $cb, array_merge( array( $value ), $args ) );
	}
	return $value;
}
function plugin_dir_path( $f ) { return dirname( $f ) . '/'; }
function plugin_dir_url( $f ) { return 'plugin/compound-index/'; }
function plugin_basename( $f ) { return basename( $f ); }
function register_deactivation_hook( $f, $c ) {}
function is_admin() { return false; }
function current_user_can( $c ) { return true; }
function locate_template( $f ) { return ''; }
function home_url( $p = '/' ) { return 'https://example.com' . $p; }
function admin_url( $p = '' ) { return 'https://example.com/wp-admin/' . $p; }

// --- options / transients ---------------------------------------------------
function get_option( $k, $d = false ) { return $GLOBALS['ci_options'][ $k ] ?? $d; }
function update_option( $k, $v, $a = true ) { $GLOBALS['ci_options'][ $k ] = $v; return true; }
function get_transient( $k ) { return $GLOBALS['ci_options'][ '_t_' . $k ] ?? false; }
function set_transient( $k, $v, $t = 0 ) { $GLOBALS['ci_options'][ '_t_' . $k ] = $v; return true; }
function register_setting( ...$a ) {}
function add_submenu_page( ...$a ) {}
function settings_fields( $g ) {}
function submit_button( $t = '' ) {}

// --- conditionals -----------------------------------------------------------
function is_shop() { return true; }
function is_product_category() { return false; }
function is_product_tag() { return false; }
function is_product_taxonomy() { return false; }
function is_search() { return false; }
function get_search_query() { return ''; }
function get_query_var( $v, $d = '' ) { return 'paged' === $v ? 1 : $d; }
function get_queried_object() { return null; }

// --- woocommerce ------------------------------------------------------------
function wc_get_page_permalink( $p ) { return 'https://example.com/shop/'; }
function wc_get_price_decimal_separator() { return '.'; }
function wc_clean( $v ) { return sanitize_text_field( $v ); }
function wc_get_loop_prop( $p, $d = '' ) { return 'total_pages' === $p ? 5 : $d; }
function wc_query_string_form_fields( ...$a ) {}
function woocommerce_page_title( $echo = true ) { return 'Shop'; }
function wc_placeholder_img( $s = '', $a = array() ) { return '<img class="ci-card__img" src="" alt="">'; }
function has_term( $t, $tax, $id ) {
	$p = $GLOBALS['ci_products'][ $id - 1 ] ?? null;
	return $p && in_array( (int) $t, $p['terms'], true );
}
function get_term( $id, $tax = '' ) { return $GLOBALS['ci_terms'][ $id ] ?? null; }
function get_term_link( $t ) { return 'https://example.com/product-category/' . $t->slug . '/'; }
function get_terms( $args = array() ) {
	$all = array_values( $GLOBALS['ci_terms'] );
	if ( ! empty( $args['include'] ) ) {
		$all = array_filter( $all, fn( $t ) => in_array( (int) $t->term_id, array_map( 'intval', $args['include'] ), true ) );
	}
	return array_values( $all );
}
function wp_count_terms( $a = array() ) { return count( $GLOBALS['ci_terms'] ); }
function get_permalink( $id ) { return 'https://example.com/product/' . $id . '/'; }
function get_the_ID() { return $GLOBALS['ci_index'] + 1; }
function get_header( $n = '' ) {}
function get_footer( $n = '' ) {}
function get_next_posts_link( $label, $max ) { return '<a href="#">' . esc_html( $label ) . '</a>'; }
function get_pagenum_link( $n, $esc = true ) { return 'https://example.com/shop/page/' . $n . '/'; }
function remove_query_arg( $k, $u ) { return $u; }
function paginate_links( $args ) {
	$out = array();
	foreach ( array( 1, 2, 3, 4 ) as $n ) {
		$cls   = 1 === $n ? 'page-numbers current' : 'page-numbers';
		$out[] = 1 === $n ? '<span class="' . $cls . '">1</span>' : '<a class="' . $cls . '" href="#">' . $n . '</a>';
	}
	$out[] = '<span class="page-numbers dots">…</span>';
	$out[] = '<a class="page-numbers" href="#">5</a>';
	return $out;
}

class WP_Term {
	public $term_id;
	public $name;
	public $slug;
	public $count;
	public $description = '';
	public function __construct( $id, $name, $slug, $count ) {
		$this->term_id = $id;
		$this->name    = $name;
		$this->slug    = $slug;
		$this->count   = $count;
	}
}

class WC_Product {
	private $data;
	public function __construct( $data ) { $this->data = $data; }
	public function get_id() { return $this->data['id']; }
	public function get_name() { return $this->data['name']; }
	public function is_visible() { return true; }
	public function get_meta( $k ) { return $this->data['meta'][ $k ] ?? ''; }
	public function get_image( $size = '', $attr = array() ) {
		return '<img class="ci-card__img" src="' . esc_attr( $this->data['img'] ) . '" alt="">';
	}
}

function wc_get_product( $id = 0 ) {
	$row = $GLOBALS['ci_products'][ $id - 1 ] ?? null;
	return $row ? new WC_Product( $row ) : null;
}

// --- loop -------------------------------------------------------------------
function have_posts() { return $GLOBALS['ci_index'] + 1 < count( $GLOBALS['ci_products'] ); }
function the_post() {
	$GLOBALS['ci_index']++;
	$GLOBALS['product'] = wc_get_product( $GLOBALS['ci_index'] + 1 );
}

// --- fake $wpdb so the stats code runs for real ------------------------------
class CI_Fake_WPDB {
	public $posts = 'wp_posts';
	public $postmeta = 'wp_postmeta';
	public $term_relationships = 'wp_term_relationships';
	public $term_taxonomy = 'wp_term_taxonomy';
	public function prepare( $sql, ...$args ) { return vsprintf( str_replace( array( '%d', '%s' ), array( '%d', "'%s'" ), $sql ), $args ); }
	public function get_var( $sql ) {
		if ( str_contains( $sql, 'pm.meta_key' ) ) { return 12; }   // products with a COA
		return 55;                                                   // published products
	}
	public function get_col( $sql ) {
		return array( '99.4%', '99.1%', '99.6%', '99.2%', '99.0%', '99.0%', '98.9%', '98.7%', '99.3%', '99.1%', '98.8%', '98.9%' );
	}
}
$GLOBALS['wpdb'] = new CI_Fake_WPDB();

// --- sample content ---------------------------------------------------------
$GLOBALS['ci_terms'] = array(
	11 => new WP_Term( 11, 'Peptides', 'peptides', 34 ),
	12 => new WP_Term( 12, 'Blends', 'blends', 9 ),
	13 => new WP_Term( 13, 'Bioregulators', 'bioregulators', 12 ),
);

$root   = dirname( __DIR__ );
$images = array();
foreach ( array( 'vial-bpc-157', 'vial-cjc-1295', 'vial-ipamorelin', 'vial-tb-500' ) as $name ) {
	$file       = $root . '/assets/images/' . $name . '.svg';
	$images[]   = is_readable( $file )
		? 'data:image/svg+xml;base64,' . base64_encode( file_get_contents( $file ) )
		: '';
}

$rows = array(
	array( 'BPC-157 · 5 mg', '137525-51-0', '1419.5 g/mol', '', '99.4%', 'B-2408-17', array( 11 ) ),
	array( 'CJC-1295 (no DAC) · 5 mg', '863288-34-0', '3647.2 g/mol', '', '99.1%', 'C-2408-04', array( 11 ) ),
	array( 'Ipamorelin · 5 mg', '170851-70-4', '711.9 g/mol', '', '99.6%', 'I-2407-22', array( 11 ) ),
	array( 'TB-500 · 5 mg', '77591-33-4', '4963.4 g/mol', '', '99.2%', 'T-2408-09', array( 11 ) ),
	array( 'CJC-1295 + Ipamorelin · 10 mg', '', '', '5 mg + 5 mg · blended 1:1', '99.0%', 'X-2407-11', array( 11, 12 ) ),
	array( 'GHK-Cu · 50 mg', '89030-95-5', '402.9 g/mol', '', '99.0%', 'G-2406-31', array( 11, 12 ) ),
	array( 'Epitalon · 10 mg', '307297-39-8', '390.3 g/mol', '', '98.9%', 'E-2408-02', array( 13 ) ),
	array( 'Thymalin · 10 mg', '', '', 'Polypeptide fraction · ~1200 g/mol', '98.7%', 'H-2407-05', array( 13 ) ),
	array( 'Semax · 10 mg', '80714-61-0', '813.9 g/mol', '', '99.3%', 'S-2407-18', array( 13 ) ),
	array( 'Selank · 10 mg', '129954-34-3', '751.9 g/mol', '', '99.1%', 'L-2406-27', array( 13 ) ),
	array( 'Pinealon · 20 mg', '', '', 'Tripeptide · 357.4 g/mol', '98.8%', 'P-2406-12', array( 13 ) ),
	array( 'GHRP-2 + CJC-1295 · 10 mg', '', '', '5 mg + 5 mg · blended 1:1', '98.9%', 'Y-2406-08', array( 11, 12 ) ),
);

foreach ( $rows as $i => $r ) {
	$GLOBALS['ci_products'][] = array(
		'id'    => $i + 1,
		'name'  => $r[0],
		'img'   => $images[ $i % count( $images ) ],
		'terms' => $r[6],
		'meta'  => array(
			'_ci_cas'        => $r[1],
			'_ci_mol_weight' => $r[2],
			'_ci_spec_line'  => $r[3],
			'_ci_purity'     => $r[4],
			'_ci_lot'        => $r[5],
			'_ci_coa_url'    => 'https://example.com/coa.pdf',
		),
	);
}

$wp_query             = new stdClass();
$wp_query->found_posts = 55;
$wp_query->post_count  = 12;
$wp_query->max_num_pages = 5;
$GLOBALS['wp_query']   = $wp_query;

// --- boot the plugin --------------------------------------------------------
require $root . '/plugin/compound-index/compound-index.php';

// The badge on blends comes from the Blends category.
$GLOBALS['ci_options']['compound_index_settings'] = array( 'badge_right_terms' => array( 12 ) );

Compound_Index_Template::init();

// --- render -----------------------------------------------------------------
ini_set( 'display_errors', '1' );
error_reporting( E_ALL );

ob_start();
include $root . '/plugin/compound-index/templates/archive-product.php';
$body = ob_get_clean();

$css = file_get_contents( $root . '/plugin/compound-index/assets/compound-index.css' );

$html = '<!doctype html><html lang="en"><head><meta charset="utf-8">'
	. '<meta name="viewport" content="width=device-width,initial-scale=1">'
	. '<title>Compound Index preview</title>'
	. '<style>body{margin:0;background:#fff}</style>'
	. '<style>' . $css . '</style></head><body>' . $body . '</body></html>';

file_put_contents( $root . '/build/archive-preview.html', $html );

echo "wrote build/archive-preview.html (" . strlen( $html ) . " bytes)\n";
