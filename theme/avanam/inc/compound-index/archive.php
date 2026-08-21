<?php
/**
 * Compound Index archive engine.
 *
 * Resolves the header from the current product category (falling back to the
 * shop defaults), builds the category chips, and reads card details from
 * existing WooCommerce product attributes. It never queries products - the grid
 * is WooCommerce's own main query.
 *
 * @package Avanam
 */

defined( 'ABSPATH' ) || exit;

/**
 * Is the Compound Index layout in charge of this request?
 *
 * @return bool
 */
function avanam_ci_is_active() {
	if ( is_admin() || ! function_exists( 'is_shop' ) ) {
		return false;
	}

	$active = is_shop() || is_product_category() || is_product_tag();

	/**
	 * Filters whether the Compound Index layout runs.
	 *
	 * @param bool $active Current decision.
	 */
	return (bool) apply_filters( 'avanam_ci_is_active', $active );
}

/**
 * The product category being viewed, if any.
 *
 * @return WP_Term|null
 */
function avanam_ci_current_term() {
	if ( ! is_product_taxonomy() ) {
		return null;
	}

	$term = get_queried_object();

	return $term instanceof WP_Term ? $term : null;
}

/**
 * A header value: the category's field, or the shop default.
 *
 * @param string $key Field key without the ci_ prefix, e.g. "title".
 * @return string
 */
function avanam_ci_header_value( $key ) {
	$term = avanam_ci_current_term();

	if ( $term ) {
		$value = avanam_ci_term_field( $term->term_id, 'ci_' . $key );
		if ( '' !== $value ) {
			return $value;
		}
	}

	return (string) avanam_ci_option( $key );
}

/**
 * Replace the {count}, {total} and {categories} tokens.
 *
 * @param string $value Raw field value.
 * @return string
 */
function avanam_ci_tokens( $value ) {
	if ( '' === $value || false === strpos( $value, '{' ) ) {
		return $value;
	}

	global $wp_query;

	$found = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : 0;
	$total = (int) wp_count_posts( 'product' )->publish;
	$cats  = wp_count_terms(
		array(
			'taxonomy'   => 'product_cat',
			'hide_empty' => true,
		)
	);

	return strtr(
		$value,
		array(
			'{count}'      => number_format_i18n( $found ),
			'{total}'      => number_format_i18n( $total ),
			'{categories}' => number_format_i18n( is_wp_error( $cats ) ? 0 : (int) $cats ),
		)
	);
}

/**
 * The header title.
 *
 * @return string
 */
function avanam_ci_title() {
	$title = avanam_ci_header_value( 'title' );

	if ( '' !== $title ) {
		return avanam_ci_tokens( $title );
	}

	$term = avanam_ci_current_term();

	return $term ? $term->name : wp_strip_all_tags( get_the_archive_title() );
}

/**
 * The header intro paragraph.
 *
 * @return string
 */
function avanam_ci_intro() {
	$intro = avanam_ci_header_value( 'intro' );

	if ( '' === $intro ) {
		$term = avanam_ci_current_term();
		if ( $term ) {
			$intro = $term->description;
		}
	}

	return avanam_ci_tokens( $intro );
}

/**
 * The header counters, ready to print.
 *
 * @return array List of array{value:string,label:string}.
 */
function avanam_ci_stats() {
	$out = array();

	for ( $i = 1; $i <= AVANAM_CI_STAT_SLOTS; $i++ ) {
		$value = avanam_ci_tokens( avanam_ci_header_value( "stat_{$i}_value" ) );
		$label = avanam_ci_header_value( "stat_{$i}_label" );

		if ( '' === $value || '' === $label ) {
			continue;
		}

		$out[] = array(
			'value' => $value,
			'label' => $label,
		);
	}

	return $out;
}

/**
 * Breadcrumb trail. The last entry has an empty url.
 *
 * @return array List of array{label:string,url:string}.
 */
function avanam_ci_breadcrumb() {
	$trail = array(
		array(
			'label' => __( 'Home', 'avanam' ),
			'url'   => home_url( '/' ),
		),
	);

	if ( avanam_ci_current_term() ) {
		$shop = wc_get_page_permalink( 'shop' );
		if ( $shop ) {
			$trail[] = array(
				'label' => __( 'Shop', 'avanam' ),
				'url'   => $shop,
			);
		}
	}

	$trail[] = array(
		'label' => avanam_ci_title(),
		'url'   => '',
	);

	return apply_filters( 'avanam_ci_breadcrumb', $trail );
}

/**
 * Category chips.
 *
 * Each is a plain link to a WooCommerce category archive, so the grid it lands
 * on is that category's real product query.
 *
 * @return array List of array{label:string,url:string,count:?int,active:bool}.
 */
function avanam_ci_chips() {
	if ( ! avanam_ci_on( 'chips' ) ) {
		return array();
	}

	$term    = avanam_ci_current_term();
	$current = $term ? (int) $term->term_id : 0;

	$chips = array(
		array(
			'label'  => avanam_ci_option( 'chips_label' ),
			'url'    => wc_get_page_permalink( 'shop' ),
			'count'  => null,
			'active' => ! $current,
		),
	);

	$args = array(
		'taxonomy'   => 'product_cat',
		// Categories you have just created have no products yet; showing them
		// anyway means a new category appears on the shop page immediately.
		'hide_empty' => avanam_ci_on( 'chips_hide_empty' ),
		'orderby'    => 'name',
	);

	$source = avanam_ci_option( 'chips_source' );

	if ( 'custom' === $source ) {
		$picked = array_filter( array_map( 'absint', (array) avanam_ci_option( 'chips_terms' ) ) );
		if ( ! $picked ) {
			return $chips;
		}
		$args['include']    = $picked;
		$args['hide_empty'] = false;
		$args['orderby']    = 'include';
	} elseif ( 'top_level' === $source ) {
		$args['parent'] = 0;
	}

	$terms = get_terms( $args );

	if ( is_wp_error( $terms ) ) {
		return $chips;
	}

	foreach ( $terms as $item ) {
		$url = get_term_link( $item );
		if ( is_wp_error( $url ) ) {
			continue;
		}

		$chips[] = array(
			'label'  => $item->name,
			'url'    => $url,
			'count'  => (int) $item->count,
			'active' => $current === (int) $item->term_id,
		);
	}

	return apply_filters( 'avanam_ci_chips', $chips );
}

/**
 * "12 of 55 shown".
 *
 * @return string
 */
function avanam_ci_result_count() {
	global $wp_query;

	$total = isset( $wp_query->found_posts ) ? (int) $wp_query->found_posts : 0;
	$shown = isset( $wp_query->post_count ) ? (int) $wp_query->post_count : 0;

	if ( ! $total ) {
		return '';
	}

	return sprintf(
		/* translators: 1: products on this page, 2: products in total. */
		__( '%1$s of %2$s shown', 'avanam' ),
		number_format_i18n( $shown ),
		number_format_i18n( $total )
	);
}

/**
 * Load the layout stylesheet only where it is used.
 */
function avanam_ci_enqueue() {
	if ( ! avanam_ci_is_active() ) {
		return;
	}

	wp_enqueue_style(
		'avanam-compound-index',
		get_template_directory_uri() . '/assets/css/compound-index.css',
		array(),
		defined( 'AVANAM_VERSION' ) ? AVANAM_VERSION : null
	);
}
add_action( 'wp_enqueue_scripts', 'avanam_ci_enqueue', 30 );

/**
 * Hide the theme's own archive title and hero here - the layout prints its own.
 *
 * @param array $layout Theme layout settings.
 * @return array
 */
function avanam_ci_hide_theme_title( $layout ) {
	if ( avanam_ci_is_active() && is_array( $layout ) ) {
		$layout['title'] = 'hide';
	}

	return $layout;
}
add_filter( 'base_post_layout', 'avanam_ci_hide_theme_title', 20 );

/**
 * Drop the theme's results-count / ordering bar, which this layout replaces.
 *
 * Only that one callback is removed, so store notices and anything a plugin
 * adds to the same hook still run.
 */
function avanam_ci_remove_theme_top_row() {
	if ( ! avanam_ci_is_active() ) {
		return;
	}

	global $wp_filter;

	if ( empty( $wp_filter['woocommerce_before_shop_loop']->callbacks[20] ) ) {
		remove_action( 'woocommerce_after_shop_loop', 'woocommerce_pagination', 10 );
		return;
	}

	// The layout prints its own pagination too.
	remove_action( 'woocommerce_after_shop_loop', 'woocommerce_pagination', 10 );

	foreach ( $wp_filter['woocommerce_before_shop_loop']->callbacks[20] as $id => $callback ) {
		if ( is_array( $callback['function'] )
			&& is_object( $callback['function'][0] )
			&& 'archive_loop_top' === $callback['function'][1] ) {
			unset( $wp_filter['woocommerce_before_shop_loop']->callbacks[20][ $id ] );
		}
	}
}
add_action( 'wp', 'avanam_ci_remove_theme_top_row', 20 );

/**
 * Let the Columns setting drive the WooCommerce loop.
 *
 * @param int $columns Current column count.
 * @return int
 */
function avanam_ci_loop_columns( $columns ) {
	if ( ! avanam_ci_is_active() ) {
		return $columns;
	}

	$set = absint( avanam_ci_option( 'columns' ) );

	return $set ? $set : $columns;
}
add_filter( 'loop_shop_columns', 'avanam_ci_loop_columns', 20 );

/**
 * Add alphabetical sorting, which the design uses and WooCommerce omits.
 *
 * WC_Query already understands "title" and "title-desc".
 *
 * @param array $options Existing sort options.
 * @return array
 */
function avanam_ci_orderby_options( $options ) {
	if ( ! avanam_ci_is_active() ) {
		return $options;
	}

	return array_merge(
		$options,
		array(
			'title'      => __( 'Name A-Z', 'avanam' ),
			'title-desc' => __( 'Name Z-A', 'avanam' ),
		)
	);
}
add_filter( 'woocommerce_catalog_orderby', 'avanam_ci_orderby_options' );
