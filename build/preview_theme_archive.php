<?php
/**
 * Render the Avanam Compound Index archive outside WordPress.
 *
 * Verification tool, not part of the deliverable. Stubs the WordPress and
 * WooCommerce functions the theme module calls, feeds it sample products and
 * category fields, and writes build/theme-archive-preview.html for screenshot
 * comparison against the reference design.
 *
 * Usage: php build/preview_theme_archive.php
 *
 * phpcs:disable
 */

define( 'ABSPATH', __DIR__ );
$root  = dirname( __DIR__ );
$theme = $root . '/theme/avanam';

$GLOBALS['ci_options']  = array();
$GLOBALS['ci_termmeta'] = array();
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
function esc_html__( $t, $d = '' ) { return esc_html( $t ); }
function esc_html_e( $t, $d = '' ) { echo esc_html( $t ); }
function esc_attr_e( $t, $d = '' ) { echo esc_attr( $t ); }
function wp_kses_post( $t ) { return $t; }
function wp_strip_all_tags( $t ) { return strip_tags( (string) $t ); }
function wp_unslash( $t ) { return $t; }
function sanitize_text_field( $t ) { return trim( strip_tags( (string) $t ) ); }
function sanitize_textarea_field( $t ) { return trim( strip_tags( (string) $t ) ); }
function sanitize_key( $t ) { return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( (string) $t ) ); }
function wpautop( $t ) { return '<p>' . trim( (string) $t ) . '</p>'; }
function number_format_i18n( $n, $d = 0 ) { return number_format( (float) $n, (int) $d ); }
function absint( $n ) { return abs( (int) $n ); }
function wp_parse_args( $a, $d = array() ) { return array_merge( $d, (array) $a ); }
function is_wp_error( $t ) { return false; }
function selected( $a, $b = true, $e = true ) { $r = ( (string) $a === (string) $b ) ? ' selected' : ''; if ( $e ) { echo $r; } return $r; }
function checked( $a, $b = true, $e = true ) { $r = $a ? ' checked' : ''; if ( $e ) { echo $r; } return $r; }

// --- hooks / theme ----------------------------------------------------------
function add_action( $h, $c, $p = 10, $a = 1 ) {}
function remove_action( $h, $c, $p = 10 ) {}
function do_action( $h, ...$a ) {}
function add_filter( $h, $c, $p = 10, $a = 1 ) { $GLOBALS['ci_filters'][ $h ][] = $c; }
function apply_filters( $h, $v, ...$a ) {
	foreach ( $GLOBALS['ci_filters'][ $h ] ?? array() as $cb ) {
		$v = call_user_func_array( $cb, array_merge( array( $v ), $a ) );
	}
	return $v;
}
function get_template_directory() { return $GLOBALS['ci_theme']; }
function get_template_directory_uri() { return 'theme/avanam'; }
function locate_template( $f ) { return ''; }
function get_header( $n = '' ) {}
function get_footer( $n = '' ) {}
function is_admin() { return false; }
function current_user_can( $c ) { return true; }
function home_url( $p = '/' ) { return 'https://example.com' . $p; }
function add_submenu_page( ...$a ) {}
function register_setting( ...$a ) {}
function settings_fields( $g ) {}
function submit_button( $t = '' ) {}
function wp_enqueue_style( ...$a ) {}

// --- options / term meta ----------------------------------------------------
function get_option( $k, $d = false ) { return $GLOBALS['ci_options'][ $k ] ?? $d; }
function update_option( $k, $v, $a = true ) { $GLOBALS['ci_options'][ $k ] = $v; return true; }
function get_term_meta( $id, $k, $single = true ) { return $GLOBALS['ci_termmeta'][ $id ][ $k ] ?? ''; }
function update_term_meta( $id, $k, $v ) { $GLOBALS['ci_termmeta'][ $id ][ $k ] = $v; }
function delete_term_meta( $id, $k ) { unset( $GLOBALS['ci_termmeta'][ $id ][ $k ] ); }

// --- query / conditionals ---------------------------------------------------
function is_shop() { return true; }
function is_product_category() { return false; }
function is_product_tag() { return false; }
function is_product_taxonomy() { return false; }
function is_search() { return false; }
function get_search_query() { return ''; }
function get_query_var( $v, $d = '' ) { return 'paged' === $v ? 1 : $d; }
function get_queried_object() { return null; }
function get_the_archive_title() { return 'Shop'; }
function have_posts() { return $GLOBALS['ci_index'] + 1 < count( $GLOBALS['ci_products'] ); }
function the_post() { $GLOBALS['ci_index']++; $GLOBALS['product'] = wc_get_product( $GLOBALS['ci_index'] + 1 ); }
function get_the_ID() { return $GLOBALS['ci_index'] + 1; }
function get_permalink( $id ) { return 'https://example.com/product/' . $id . '/'; }
function get_pagenum_link( $n, $e = true ) { return 'https://example.com/shop/page/' . $n . '/'; }
function remove_query_arg( $k, $u ) { return $u; }
function get_next_posts_link( $l, $m ) { return '<a href="#">' . esc_html( $l ) . '</a>'; }
function paginate_links( $args ) {
	$out = array();
	foreach ( array( 1, 2, 3, 4 ) as $n ) {
		$out[] = 1 === $n
			? '<span class="page-numbers current">1</span>'
			: '<a class="page-numbers" href="#">' . $n . '</a>';
	}
	$out[] = '<span class="page-numbers dots">&hellip;</span>';
	$out[] = '<a class="page-numbers" href="#">5</a>';
	return $out;
}
function wp_count_posts( $t ) { return (object) array( 'publish' => 55 ); }
function wp_count_terms( $a = array() ) { return count( $GLOBALS['ci_terms'] ); }

// --- terms ------------------------------------------------------------------
class WP_Term {
	public $term_id, $name, $slug, $count, $description = '';
	public function __construct( $id, $name, $slug, $count ) {
		$this->term_id = $id; $this->name = $name; $this->slug = $slug; $this->count = $count;
	}
}
function get_terms( $a = array() ) { return array_values( $GLOBALS['ci_terms'] ); }
function get_term_link( $t ) { return 'https://example.com/product-category/' . $t->slug . '/'; }
function get_the_terms( $id, $tax ) {
	$row = $GLOBALS['ci_products'][ $id - 1 ] ?? null;
	if ( ! $row ) { return array(); }
	return array_values( array_intersect_key( $GLOBALS['ci_terms'], array_flip( $row['terms'] ) ) );
}

// --- woocommerce ------------------------------------------------------------
function wc_get_page_permalink( $p ) { return 'https://example.com/shop/'; }
function wc_get_loop_prop( $p, $d = '' ) { return 'columns' === $p ? 4 : $d; }
function woocommerce_product_loop() { return count( $GLOBALS['ci_products'] ) > 0; }
function woocommerce_product_loop_start() {
	// Mirrors Avanam\'s Woocommerce::product_loop_start() output.
	echo '<ul class="products content-wrap product-archive grid-cols grid-ss-col-2 grid-sm-col-3 grid-lg-col-4'
		. ' woo-archive-normal woo-archive-btn-normal woo-archive-loop align-buttons-bottom'
		. ' woo-archive-image-hover-none">';
}
function woocommerce_product_loop_end() { echo '</ul>'; }
function wc_get_template_part( $slug, $name = '' ) {
	// Mirrors the markup Avanam builds around WooCommerce\'s content-product.php.
	$p    = $GLOBALS['product'];
	$row  = $GLOBALS['ci_products'][ $p->get_id() - 1 ];
	$full = 3 === $p->get_id() % 4;
	$stars = '';
	for ( $i = 0; $i < 5; $i++ ) { $stars .= $full ? '&#9733;' : '&#9734;'; }
	echo '<li class="product type-product status-publish instock has-post-thumbnail purchasable'
		. ' product-type-simple entry content-bg loop-entry">'
		. '<div class="product-thumbnail">'
			. '<a href="#"><img src="' . esc_attr( $row['img'] ) . '" alt=""></a>'
			. '<div class="product-actions"></div>'
		. '</div>'
		. '<div class="product-details content-bg entry-content-wrap">'
			. '<h2 class="woocommerce-loop-product__title"><a href="#">' . esc_html( $p->get_name() ) . '</a></h2>'
			. '<div class="star-rating">' . $stars . '</div>'
			. '<span class="price"><span class="woocommerce-Price-amount amount">' . esc_html( $p->get_price_html() ) . '</span></span>'
			. '<div class="product-action-wrap style-normal">'
				. '<a href="#" class="button product_type_simple add_to_cart_button">Add to cart</a>'
			. '</div>'
		. '</div>'
		. '</li>';
}
function wc_clean( $v ) { return sanitize_text_field( $v ); }
function wc_query_string_form_fields( ...$a ) {}
function wc_placeholder_img( $s = '', $a = array() ) { return '<img class="ci-card__img" src="" alt="">'; }
function wc_attribute_label( $tax ) { return $GLOBALS['ci_attr_labels'][ $tax ] ?? $tax; }
function wc_get_attribute_taxonomies() { return array(); }
function wc_attribute_taxonomy_name( $n ) { return 'pa_' . $n; }

class WC_Product {
	private $d;
	public function __construct( $d ) { $this->d = $d; }
	public function get_id() { return $this->d['id']; }
	public function get_name() { return $this->d['name']; }
	public function is_visible() { return true; }
	public function get_price_html() { return '$14'; }
	public function get_attribute( $tax ) { return $this->d['attrs'][ $tax ] ?? ''; }
	public function get_image( $s = '', $a = array() ) {
		return '<img class="ci-card__img" src="' . esc_attr( $this->d['img'] ) . '" alt="">';
	}
}
function wc_get_product( $id = 0 ) {
	$row = $GLOBALS['ci_products'][ $id - 1 ] ?? null;
	return $row ? new WC_Product( $row ) : null;
}

// --- sample content ---------------------------------------------------------
$GLOBALS['ci_theme']       = $theme;
$GLOBALS['ci_attr_labels'] = array(
	'pa_cas'      => 'CAS',
	'pa_mass'     => 'Molecular weight',
	'pa_purity'   => 'Purity',
	'pa_latest-lot' => 'Latest lot',
);
$GLOBALS['ci_terms'] = array(
	11 => new WP_Term( 11, 'Peptides', 'peptides', 34 ),
	12 => new WP_Term( 12, 'Blends', 'blends', 9 ),
	13 => new WP_Term( 13, 'Bioregulators', 'bioregulators', 12 ),
);
// "Card badge" field on the Blends category.
$GLOBALS['ci_termmeta'][12]['ci_badge'] = 'Blend';

$images = array();
foreach ( array( 'vial-bpc-157', 'vial-cjc-1295', 'vial-ipamorelin', 'vial-tb-500' ) as $n ) {
	$f = $root . '/assets/images/' . $n . '.svg';
	if ( ! is_readable( $f ) ) { $images[] = ''; continue; }
	// The sample vials are tall and narrow; real product photos are roughly
	// square, so pad the viewBox to a square for a representative preview.
	$svg = file_get_contents( $f );
	$svg = str_replace(
		array( 'viewBox="44 0 112 190"', 'width="112" height="190"' ),
		array( 'viewBox="5 0 190 190"', 'width="190" height="190"' ),
		$svg
	);
	$images[] = 'data:image/svg+xml;base64,' . base64_encode( $svg );
}

$rows = array(
	array( 'Testing-4', '137525-51-0', '1419.5 g/mol', '99.4%', 'B-2408-17', array( 11 ) ),
	array( 'Testing-3', '863288-34-0', '3647.2 g/mol', '99.1%', 'C-2408-04', array( 11 ) ),
	array( 'Testing-1', '170851-70-4', '711.9 g/mol', '99.6%', 'I-2407-22', array( 11 ) ),
	array( 'Testing-2', '77591-33-4', '4963.4 g/mol', '99.2%', 'T-2408-09', array( 11 ) ),
	array( 'CJC-1295 + Ipamorelin · 10 mg', '', '5 mg + 5 mg · blended 1:1', '99.0%', 'X-2407-11', array( 11, 12 ) ),
	array( 'GHK-Cu · 50 mg', '89030-95-5', '402.9 g/mol', '99.0%', 'G-2406-31', array( 11, 12 ) ),
	array( 'Epitalon · 10 mg', '307297-39-8', '390.3 g/mol', '98.9%', 'E-2408-02', array( 13 ) ),
	array( 'Thymalin · 10 mg', '', 'Polypeptide fraction', '98.7%', 'H-2407-05', array( 13 ) ),
	array( 'Semax · 10 mg', '80714-61-0', '813.9 g/mol', '99.3%', 'S-2407-18', array( 13 ) ),
	array( 'Selank · 10 mg', '129954-34-3', '751.9 g/mol', '99.1%', 'L-2406-27', array( 13 ) ),
	array( 'Pinealon · 20 mg', '', 'Tripeptide · 357.4 g/mol', '98.8%', 'P-2406-12', array( 13 ) ),
	array( 'GHRP-2 + CJC-1295 · 10 mg', '', '5 mg + 5 mg · blended 1:1', '98.9%', 'Y-2406-08', array( 11, 12 ) ),
);

foreach ( $rows as $i => $r ) {
	$GLOBALS['ci_products'][] = array(
		'id'    => $i + 1,
		'name'  => $r[0],
		'img'   => $images[ $i % count( $images ) ],
		'terms' => $r[5],
		'attrs' => array(
			'pa_cas'        => $r[1] ? 'CAS ' . $r[1] : '',
			'pa_mass'       => $r[2],
			'pa_purity'     => $r[3],
			'pa_latest-lot' => $r[4],
		),
	);
}

$wp_query                = new stdClass();
$wp_query->found_posts   = 55;
$wp_query->post_count    = 12;
$wp_query->max_num_pages = 5;
$GLOBALS['wp_query']     = $wp_query;

// --- boot the theme module --------------------------------------------------
require $theme . '/inc/compound-index/compound-index.php';

// Shop-page settings, as an admin would have saved them.
$GLOBALS['ci_options']['avanam_compound_index'] = array(
	'stat_2_value' => '99.2%',
	'stat_3_value' => '100%',
	'stat_4_value' => '36 mo',
	'spec_attrs'   => array( 'pa_cas', 'pa_mass' ),
	'row_attrs'    => array( 'pa_purity', 'pa_latest-lot' ),
);

ini_set( 'display_errors', '1' );
error_reporting( E_ALL );

ob_start();
include $theme . '/woocommerce/archive-product.php';
$body = ob_get_clean();

$css  = file_get_contents( $theme . '/assets/css/compound-index.css' );
$html = '<!doctype html><html lang="en"><head><meta charset="utf-8">'
	. '<meta name="viewport" content="width=device-width,initial-scale=1">'
	. '<title>Avanam - Compound Index preview</title>'
	// Mimic the theme's own page container so widths match the real site.
	// Stand-in for the Avanam base styles the archive sits on.
	. '<style>' . file_get_contents( __DIR__ . '/preview-theme-shim.css' ) . '</style>'
	. '<style>' . $css . '</style></head>'
	. '<body class="woocommerce post-type-archive post-type-archive-product">'
	. '<div class="site-container">'
	. $body . '</div></body></html>';

file_put_contents( $root . '/build/theme-archive-preview.html', $html );

echo 'wrote build/theme-archive-preview.html (' . strlen( $html ) . " bytes)\n";
