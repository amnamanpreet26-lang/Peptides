<?php
/**
 * Numbered pagination.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

global $wp_query;

$ci_total = isset( $wp_query->max_num_pages ) ? (int) $wp_query->max_num_pages : 0;

if ( $ci_total < 2 ) {
	return;
}

$ci_links = paginate_links(
	array(
		'base'      => esc_url_raw( str_replace( 999999999, '%#%', remove_query_arg( 'add-to-cart', get_pagenum_link( 999999999, false ) ) ) ),
		'format'    => '',
		'total'     => $ci_total,
		'current'   => max( 1, get_query_var( 'paged' ) ),
		'type'      => 'array',
		'end_size'  => 1,
		'mid_size'  => 1,
		'prev_next' => false,
	)
);

if ( ! $ci_links ) {
	return;
}
?>
<nav class="ci-pager" aria-label="<?php esc_attr_e( 'Product pages', 'avanam' ); ?>">
	<?php
	foreach ( $ci_links as $ci_link ) {
		echo wp_kses_post( $ci_link );
	}

	$ci_next = get_next_posts_link( __( 'Next', 'avanam' ), $ci_total );
	if ( $ci_next ) {
		echo '<span class="ci-pager__next">' . wp_kses_post( $ci_next ) . '<span aria-hidden="true"> &rarr;</span></span>';
	}
	?>
</nav>
