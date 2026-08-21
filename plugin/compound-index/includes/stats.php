<?php
/**
 * Works out the numbers behind the four header counters.
 *
 * Anything that needs a database scan is cached for twelve hours behind a
 * version stamp, so saving a product or the settings invalidates every cached
 * figure at once without having to track individual transient keys.
 *
 * @package Compound_Index
 */

defined( 'ABSPATH' ) || exit;

/**
 * Counter value resolution.
 */
class Compound_Index_Stats {

	const VERSION_OPTION = 'compound_index_stats_version';
	const TTL            = 12 * HOUR_IN_SECONDS;

	/**
	 * Bump the cache stamp, invalidating every cached figure.
	 */
	public static function flush_cache() {
		update_option( self::VERSION_OPTION, (string) time(), false );
	}

	/**
	 * Current cache stamp.
	 *
	 * @return string
	 */
	private static function version() {
		$v = get_option( self::VERSION_OPTION );
		if ( ! $v ) {
			$v = (string) time();
			update_option( self::VERSION_OPTION, $v, false );
		}
		return $v;
	}

	/**
	 * Read through the cache.
	 *
	 * @param string   $key      Cache key fragment.
	 * @param callable $resolver Produces the value on a miss.
	 * @return mixed
	 */
	private static function cached( $key, callable $resolver ) {
		$transient = 'ci_stat_' . md5( self::version() . '|' . $key );
		$hit       = get_transient( $transient );

		if ( false !== $hit && is_array( $hit ) && array_key_exists( 'v', $hit ) ) {
			return $hit['v'];
		}

		$value = $resolver();
		set_transient( $transient, array( 'v' => $value ), self::TTL );

		return $value;
	}

	/**
	 * The product category currently being viewed, if any.
	 *
	 * @return int Term ID, or 0 on the shop page.
	 */
	private static function current_term_id() {
		if ( function_exists( 'is_product_taxonomy' ) && is_product_taxonomy() ) {
			$term = get_queried_object();
			if ( $term instanceof WP_Term ) {
				return (int) $term->term_id;
			}
		}
		return 0;
	}

	/**
	 * Format a resolved figure for display.
	 *
	 * @param array $stat One counter's settings.
	 * @return string Empty string when there is nothing to show.
	 */
	public static function display( array $stat ) {
		$suffix = isset( $stat['suffix'] ) ? $stat['suffix'] : '';

		if ( 'manual' === $stat['source'] ) {
			$value = trim( (string) $stat['value'] );
			return '' === $value ? '' : $value . $suffix;
		}

		$raw = self::resolve( $stat );
		if ( null === $raw ) {
			return '';
		}

		$decimals = isset( $stat['decimals'] ) ? (int) $stat['decimals'] : 0;
		$number   = number_format_i18n( $raw, $decimals );

		// 99.0 reads better as 99 - drop a decimal part that is all zeros.
		if ( $decimals > 0 ) {
			$sep    = wc_get_price_decimal_separator();
			$number = preg_replace( '/' . preg_quote( $sep, '/' ) . '0+$/', '', $number );
		}

		return $number . $suffix;
	}

	/**
	 * Resolve a counter to a number.
	 *
	 * @param array $stat One counter's settings.
	 * @return float|int|null
	 */
	public static function resolve( array $stat ) {
		$term_id  = self::current_term_id();
		$meta_key = isset( $stat['meta_key'] ) ? $stat['meta_key'] : '';

		switch ( $stat['source'] ) {
			case 'product_count':
				// The archive query has already counted these - no extra work.
				$found = isset( $GLOBALS['wp_query'] ) ? (int) $GLOBALS['wp_query']->found_posts : 0;
				return $found > 0 ? $found : self::cached( "catalog|{$term_id}", fn() => self::count_products( $term_id ) );

			case 'catalog_count':
				return self::cached( 'catalog|0', fn() => self::count_products( 0 ) );

			case 'term_count':
				return self::cached( 'terms', fn() => self::count_terms() );

			case 'meta_avg':
			case 'meta_median':
			case 'meta_filled_pct':
				if ( '' === $meta_key ) {
					return null;
				}
				return self::cached(
					"{$stat['source']}|{$meta_key}|{$term_id}",
					function () use ( $stat, $meta_key, $term_id ) {
						if ( 'meta_filled_pct' === $stat['source'] ) {
							$total = self::count_products( $term_id );
							if ( ! $total ) {
								return null;
							}
							return ( self::count_filled( $meta_key, $term_id ) / $total ) * 100;
						}

						$values = self::meta_numbers( $meta_key, $term_id );
						if ( ! $values ) {
							return null;
						}
						return 'meta_avg' === $stat['source']
							? array_sum( $values ) / count( $values )
							: self::median( $values );
					}
				);
		}

		return null;
	}

	/**
	 * Published product count, optionally inside one category.
	 *
	 * @param int $term_id Product category, or 0 for the whole catalogue.
	 * @return int
	 */
	private static function count_products( $term_id = 0 ) {
		global $wpdb;

		if ( $term_id ) {
			return (int) $wpdb->get_var(
				$wpdb->prepare(
					"SELECT COUNT(DISTINCT p.ID)
					 FROM {$wpdb->posts} p
					 INNER JOIN {$wpdb->term_relationships} tr ON tr.object_id = p.ID
					 INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_taxonomy_id = tr.term_taxonomy_id
					 WHERE p.post_type = 'product' AND p.post_status = 'publish'
					   AND tt.taxonomy = 'product_cat' AND tt.term_id = %d",
					$term_id
				)
			);
		}

		return (int) $wpdb->get_var(
			"SELECT COUNT(ID) FROM {$wpdb->posts} WHERE post_type = 'product' AND post_status = 'publish'"
		);
	}

	/**
	 * How many published products have a non-empty value for a field.
	 *
	 * @param string $meta_key Meta key.
	 * @param int    $term_id  Product category, or 0.
	 * @return int
	 */
	private static function count_filled( $meta_key, $term_id = 0 ) {
		global $wpdb;

		$join  = '';
		$where = '';
		if ( $term_id ) {
			$join  = "INNER JOIN {$wpdb->term_relationships} tr ON tr.object_id = p.ID
				 INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_taxonomy_id = tr.term_taxonomy_id";
			$where = $wpdb->prepare( " AND tt.taxonomy = 'product_cat' AND tt.term_id = %d", $term_id );
		}

		// phpcs:disable WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- fragments above are prepared or literal.
		return (int) $wpdb->get_var(
			$wpdb->prepare(
				"SELECT COUNT(DISTINCT p.ID)
				 FROM {$wpdb->posts} p
				 INNER JOIN {$wpdb->postmeta} pm ON pm.post_id = p.ID
				 {$join}
				 WHERE p.post_type = 'product' AND p.post_status = 'publish'
				   AND pm.meta_key = %s AND pm.meta_value <> ''
				 {$where}",
				$meta_key
			)
		);
		// phpcs:enable
	}

	/**
	 * Numeric values of a product field across published products.
	 *
	 * Values are stored as text ("99.4%", "1419.5 g/mol"), so the leading number
	 * is parsed out and anything non-numeric is dropped.
	 *
	 * @param string $meta_key Meta key.
	 * @param int    $term_id  Product category, or 0.
	 * @return float[]
	 */
	private static function meta_numbers( $meta_key, $term_id = 0 ) {
		global $wpdb;

		$join  = '';
		$where = '';
		if ( $term_id ) {
			$join  = "INNER JOIN {$wpdb->term_relationships} tr ON tr.object_id = p.ID
				 INNER JOIN {$wpdb->term_taxonomy} tt ON tt.term_taxonomy_id = tr.term_taxonomy_id";
			$where = $wpdb->prepare( " AND tt.taxonomy = 'product_cat' AND tt.term_id = %d", $term_id );
		}

		// phpcs:disable WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- fragments above are prepared or literal.
		$rows = $wpdb->get_col(
			$wpdb->prepare(
				"SELECT pm.meta_value
				 FROM {$wpdb->posts} p
				 INNER JOIN {$wpdb->postmeta} pm ON pm.post_id = p.ID
				 {$join}
				 WHERE p.post_type = 'product' AND p.post_status = 'publish'
				   AND pm.meta_key = %s AND pm.meta_value <> ''
				 {$where}",
				$meta_key
			)
		);
		// phpcs:enable

		$numbers = array();
		foreach ( (array) $rows as $row ) {
			$clean = preg_replace( '/[^0-9.\-]/', '', (string) $row );
			if ( '' !== $clean && is_numeric( $clean ) ) {
				$numbers[] = (float) $clean;
			}
		}

		return $numbers;
	}

	/**
	 * Product categories that hold at least one product.
	 *
	 * @return int
	 */
	private static function count_terms() {
		$count = wp_count_terms(
			array(
				'taxonomy'   => 'product_cat',
				'hide_empty' => true,
			)
		);

		return is_wp_error( $count ) ? 0 : (int) $count;
	}

	/**
	 * Median of a list of numbers.
	 *
	 * @param float[] $values Numbers.
	 * @return float
	 */
	private static function median( array $values ) {
		sort( $values );
		$count  = count( $values );
		$middle = (int) floor( ( $count - 1 ) / 2 );

		if ( $count % 2 ) {
			return $values[ $middle ];
		}

		return ( $values[ $middle ] + $values[ $middle + 1 ] ) / 2;
	}
}

// Keep the figures honest as the catalogue changes.
add_action( 'save_post_product', array( 'Compound_Index_Stats', 'flush_cache' ) );
add_action( 'deleted_post', array( 'Compound_Index_Stats', 'flush_cache' ) );
add_action( 'edited_product_cat', array( 'Compound_Index_Stats', 'flush_cache' ) );
add_action( 'created_product_cat', array( 'Compound_Index_Stats', 'flush_cache' ) );
